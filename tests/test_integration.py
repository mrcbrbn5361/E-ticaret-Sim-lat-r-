#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration Tests
End-to-end testing of complete user workflows
"""

import pytest
import os
import tempfile
from app import create_app, db
from models.user import User
from models.product import Product, Category
from models.order import CartItem, Order, OrderItem
from models.review import Review

@pytest.fixture
def app():
    """Create test application with sample data"""
    db_fd, db_path = tempfile.mkstemp()
    
    test_app = create_app()
    test_app.config['TESTING'] = True
    test_app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    test_app.config['WTF_CSRF_ENABLED'] = False
    
    with test_app.app_context():
        db.create_all()
        
        # Create test categories
        electronics = Category(name='Elektronik', description='Electronics category')
        clothing = Category(name='Giyim', description='Clothing category')
        db.session.add_all([electronics, clothing])
        db.session.flush()
        
        # Create test products
        iphone = Product(
            name='iPhone 15 Pro',
            description='Latest iPhone model',
            price=45000.0,
            original_price=50000.0,
            stock_quantity=10,
            category_id=electronics.id,
            brand='Apple',
            is_featured=True,
            rating=4.5,
            review_count=25
        )
        
        macbook = Product(
            name='MacBook Air M2',
            description='Powerful laptop',
            price=35000.0,
            stock_quantity=5,
            category_id=electronics.id,
            brand='Apple',
            is_featured=True
        )
        
        tshirt = Product(
            name='Cotton T-Shirt',
            description='Comfortable cotton t-shirt',
            price=150.0,
            stock_quantity=20,
            category_id=clothing.id,
            brand='TestBrand'
        )
        
        db.session.add_all([iphone, macbook, tshirt])
        db.session.flush()
        
        # Create test users
        regular_user = User(
            username='customer',
            email='customer@example.com',
            first_name='John',
            last_name='Doe',
            phone='05551234567',
            address='Test Address 123',
            city='Istanbul'
        )
        regular_user.set_password('customer123')
        
        admin_user = User(
            username='admin',
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            is_admin=True
        )
        admin_user.set_password('admin123')
        
        db.session.add_all([regular_user, admin_user])
        db.session.commit()
        
        yield test_app
        
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

class TestCompleteUserJourney:
    """Test complete user journey from registration to order completion"""
    
    def test_new_user_registration_and_shopping(self, client, app):
        """Test complete new user journey"""
        with app.app_context():
            # Step 1: User visits homepage
            response = client.get('/')
            assert response.status_code == 200
            assert 'TrendyolApp' in response.data.decode('utf-8')
            
            # Step 2: User registers
            response = client.post('/auth/kayit', data={
                'username': 'newcustomer',
                'email': 'newcustomer@example.com',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'phone': '05559876543',
                'password': 'newuser123',
                'password_confirm': 'newuser123'
            }, follow_redirects=True)
            assert response.status_code == 200
            
            # Verify user was created
            user = User.query.filter_by(username='newcustomer').first()
            assert user is not None
            assert user.email == 'newcustomer@example.com'
            
            # Step 3: User logs in
            response = client.post('/auth/giris', data={
                'username': 'newcustomer',
                'password': 'newuser123'
            }, follow_redirects=True)
            assert response.status_code == 200
            
            # Step 4: User browses products
            response = client.get('/urunler/')
            assert response.status_code == 200
            
            # Step 5: User views product details
            iphone = Product.query.filter_by(name='iPhone 15 Pro').first()
            response = client.get(f'/urunler/{iphone.id}')
            assert response.status_code == 200
            assert 'iPhone 15 Pro' in response.data.decode('utf-8')
            
            # Step 6: User adds product to cart
            response = client.post(f'/sepet/ekle/{iphone.id}', data={
                'quantity': 1
            }, follow_redirects=True)
            assert response.status_code == 200
            
            # Verify cart item was created
            cart_item = CartItem.query.filter_by(user_id=user.id, product_id=iphone.id).first()
            assert cart_item is not None
            assert cart_item.quantity == 1
            
            # Step 7: User views cart
            response = client.get('/sepet/')
            assert response.status_code == 200
            assert 'iPhone 15 Pro' in response.data.decode('utf-8')
            
            # Step 8: User proceeds to checkout
            response = client.get('/sepet/odeme')
            assert response.status_code == 200
            
            # Step 9: User places order
            response = client.post('/sepet/siparis-ver', data={
                'shipping_address': 'New Address 456, Ankara',
                'payment_method': 'Kredi Kartı',
                'notes': 'Please deliver carefully'
            }, follow_redirects=True)
            assert response.status_code == 200
            
            # Verify order was created
            order = Order.query.filter_by(user_id=user.id).first()
            assert order is not None
            assert order.shipping_address == 'New Address 456, Ankara'
            assert order.payment_method == 'Kredi Kartı'
            
            # Verify order items
            order_item = OrderItem.query.filter_by(order_id=order.id).first()
            assert order_item is not None
            assert order_item.product_id == iphone.id
            assert order_item.quantity == 1
            
            # Verify cart was cleared
            remaining_cart_items = CartItem.query.filter_by(user_id=user.id).count()
            assert remaining_cart_items == 0
            
            # Verify stock was reduced
            updated_iphone = Product.query.get(iphone.id)
            assert updated_iphone.stock_quantity == 9  # Was 10, now 9
    
    def test_existing_user_repeat_purchase(self, client, app):
        """Test existing user making repeat purchases"""
        with app.app_context():
            # Login existing user
            response = client.post('/auth/giris', data={
                'username': 'customer',
                'password': 'customer123'
            }, follow_redirects=True)
            assert response.status_code == 200
            
            user = User.query.filter_by(username='customer').first()
            macbook = Product.query.filter_by(name='MacBook Air M2').first()
            tshirt = Product.query.filter_by(name='Cotton T-Shirt').first()
            
            # Add multiple products to cart
            client.post(f'/sepet/ekle/{macbook.id}', data={'quantity': 1})
            client.post(f'/sepet/ekle/{tshirt.id}', data={'quantity': 3})
            
            # Verify cart contents
            cart_items = CartItem.query.filter_by(user_id=user.id).all()
            assert len(cart_items) == 2
            
            total_cart_value = sum(item.get_total_price() for item in cart_items)
            expected_total = (35000.0 * 1) + (150.0 * 3)  # MacBook + 3 T-shirts
            assert total_cart_value == expected_total
            
            # Place order
            response = client.post('/sepet/siparis-ver', data={
                'shipping_address': user.address,
                'payment_method': 'Kapıda Ödeme'
            }, follow_redirects=True)
            assert response.status_code == 200
            
            # Verify order
            order = Order.query.filter_by(user_id=user.id).first()
            assert order is not None
            assert order.get_item_count() == 4  # 1 MacBook + 3 T-shirts
    
    def test_user_product_review_flow(self, client, app):
        """Test user reviewing purchased products"""
        with app.app_context():
            # Login user
            client.post('/auth/giris', data={
                'username': 'customer',
                'password': 'customer123'
            })
            
            user = User.query.filter_by(username='customer').first()
            iphone = Product.query.filter_by(name='iPhone 15 Pro').first()
            
            # User adds review
            response = client.post(f'/urunler/{iphone.id}/yorum-ekle', data={
                'rating': 5,
                'title': 'Excellent phone!',
                'comment': 'Great camera quality and performance. Highly recommended!'
            }, follow_redirects=True)
            assert response.status_code == 200
            
            # Verify review was created
            review = Review.query.filter_by(user_id=user.id, product_id=iphone.id).first()
            assert review is not None
            assert review.rating == 5
            assert review.title == 'Excellent phone!'
            assert review.is_approved == True
            
            # Test duplicate review prevention
            response = client.post(f'/urunler/{iphone.id}/yorum-ekle', data={
                'rating': 4,
                'title': 'Another review',
                'comment': 'This should not be allowed'
            }, follow_redirects=True)
            assert response.status_code == 200
            assert 'zaten yorum yapmışsınız' in response.data.decode('utf-8')
            
            # Verify only one review exists
            review_count = Review.query.filter_by(user_id=user.id, product_id=iphone.id).count()
            assert review_count == 1

class TestAdminWorkflow:
    """Test admin workflow and management features"""
    
    def test_admin_product_management(self, client, app):
        """Test admin product management workflow"""
        with app.app_context():
            # Login as admin
            response = client.post('/auth/giris', data={
                'username': 'admin',
                'password': 'admin123'
            }, follow_redirects=True)
            assert response.status_code == 200
            
            # Access admin dashboard
            response = client.get('/admin/')
            assert response.status_code == 200
            
            # View products
            response = client.get('/admin/urunler')
            assert response.status_code == 200
            
            # Add new product
            electronics = Category.query.filter_by(name='Elektronik').first()
            response = client.post('/admin/urunler/ekle', data={
                'name': 'Samsung Galaxy S24',
                'description': 'Latest Samsung flagship phone',
                'price': 40000.0,
                'original_price': 42000.0,
                'stock_quantity': 15,
                'category_id': electronics.id,
                'brand': 'Samsung',
                'color': 'Black',
                'is_featured': True
            }, follow_redirects=True)
            assert response.status_code == 200
            
            # Verify product was created
            samsung = Product.query.filter_by(name='Samsung Galaxy S24').first()
            assert samsung is not None
            assert samsung.brand == 'Samsung'
            assert samsung.is_featured == True
            
            # Edit product
            response = client.post(f'/admin/urunler/{samsung.id}/duzenle', data={
                'name': 'Samsung Galaxy S24 Ultra',
                'description': 'Premium Samsung flagship phone',
                'price': 45000.0,
                'original_price': 47000.0,
                'stock_quantity': 12,
                'category_id': electronics.id,
                'brand': 'Samsung',
                'color': 'Black',
                'is_featured': True,
                'is_active': True
            }, follow_redirects=True)
            assert response.status_code == 200
            
            # Verify product was updated
            updated_samsung = Product.query.get(samsung.id)
            assert updated_samsung.name == 'Samsung Galaxy S24 Ultra'
            assert updated_samsung.price == 45000.0
    
    def test_admin_order_management(self, client, app):
        """Test admin order management"""
        with app.app_context():
            # Create test order first
            user = User.query.filter_by(username='customer').first()
            iphone = Product.query.filter_by(name='iPhone 15 Pro').first()
            
            order = Order(
                order_number='TEST202401001',
                user_id=user.id,
                total_amount=45015.0,  # iPhone + shipping
                shipping_address='Test Address',
                payment_method='Kredi Kartı',
                status='Beklemede'
            )
            db.session.add(order)
            db.session.flush()
            
            order_item = OrderItem(
                order_id=order.id,
                product_id=iphone.id,
                quantity=1,
                unit_price=45000.0,
                total_price=45000.0
            )
            db.session.add(order_item)
            db.session.commit()
            
            # Login as admin
            client.post('/auth/giris', data={
                'username': 'admin',
                'password': 'admin123'
            })
            
            # View orders
            response = client.get('/admin/siparisler')
            assert response.status_code == 200
            assert 'TEST202401001' in response.data.decode('utf-8')
            
            # Update order status
            response = client.post(f'/admin/siparisler/{order.id}/duzenle', data={
                'status': 'Onaylandı'
            }, follow_redirects=True)
            assert response.status_code == 200
            
            # Verify status was updated
            updated_order = Order.query.get(order.id)
            assert updated_order.status == 'Onaylandı'
            
            # Update to shipped
            response = client.post(f'/admin/siparisler/{order.id}/duzenle', data={
                'status': 'Kargoda'
            }, follow_redirects=True)
            assert response.status_code == 200
            
            updated_order = Order.query.get(order.id)
            assert updated_order.status == 'Kargoda'
            assert updated_order.shipped_at is not None

class TestErrorScenarios:
    """Test error scenarios and edge cases"""
    
    def test_insufficient_stock_scenario(self, client, app):
        """Test ordering more than available stock"""
        with app.app_context():
            # Login user
            client.post('/auth/giris', data={
                'username': 'customer',
                'password': 'customer123'
            })
            
            # Find product with limited stock
            macbook = Product.query.filter_by(name='MacBook Air M2').first()
            assert macbook.stock_quantity == 5
            
            # Try to add more than available stock
            response = client.post(f'/sepet/ekle/{macbook.id}', data={
                'quantity': 10  # More than stock
            }, follow_redirects=True)
            assert response.status_code == 200
            assert 'stokta sadece' in response.data.decode('utf-8').lower() or 'yeterli stok' in response.data.decode('utf-8').lower()
    
    def test_cart_persistence_across_sessions(self, client, app):
        """Test that cart items persist across user sessions"""
        with app.app_context():
            # Login and add item to cart
            client.post('/auth/giris', data={
                'username': 'customer',
                'password': 'customer123'
            })
            
            user = User.query.filter_by(username='customer').first()
            tshirt = Product.query.filter_by(name='Cotton T-Shirt').first()
            
            client.post(f'/sepet/ekle/{tshirt.id}', data={'quantity': 2})
            
            # Logout
            client.get('/auth/cikis')
            
            # Login again
            client.post('/auth/giris', data={
                'username': 'customer',
                'password': 'customer123'
            })
            
            # Check cart still has items
            response = client.get('/sepet/')
            assert response.status_code == 200
            assert 'Cotton T-Shirt' in response.data.decode('utf-8')
            
            # Verify in database
            cart_items = CartItem.query.filter_by(user_id=user.id).all()
            assert len(cart_items) == 1
            assert cart_items[0].quantity == 2

if __name__ == '__main__':
    pytest.main([__file__, '-v'])