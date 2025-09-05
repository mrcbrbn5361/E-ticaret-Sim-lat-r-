#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Routes and Application Tests
Test cases for web routes, forms, and application functionality
"""

import pytest
import os
import tempfile
from app import create_app, db
from models.user import User
from models.product import Product, Category
from models.order import CartItem, Order
from models.review import Review

@pytest.fixture
def app():
    """Create test application"""
    db_fd, db_path = tempfile.mkstemp()
    
    test_app = create_app()
    test_app.config['TESTING'] = True
    test_app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    test_app.config['WTF_CSRF_ENABLED'] = False
    
    with test_app.app_context():
        db.create_all()
        
        # Create test data
        category = Category(name='Test Category', description='Test description')
        db.session.add(category)
        db.session.flush()
        
        product = Product(
            name='Test Product',
            description='Test product description',
            price=1000.0,
            stock_quantity=10,
            category_id=category.id,
            is_featured=True
        )
        db.session.add(product)
        
        user = User(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        user.set_password('testpass')
        db.session.add(user)
        
        admin = User(
            username='admin',
            email='admin@test.com',
            first_name='Admin',
            last_name='User',
            is_admin=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        db.session.commit()
        
        yield test_app
        
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

def login_user(client, username='testuser', password='testpass'):
    """Helper function to login user"""
    return client.post('/auth/giris', data={
        'username': username,
        'password': password
    }, follow_redirects=True)

def login_admin(client):
    """Helper function to login admin"""
    return login_user(client, 'admin', 'admin123')

class TestMainRoutes:
    """Test main application routes"""
    
    def test_homepage(self, client):
        """Test homepage access"""
        response = client.get('/')
        assert response.status_code == 200
        assert 'TrendyolApp' in response.data.decode('utf-8')
        assert 'Kategoriler' in response.data.decode('utf-8')
        assert 'Öne Çıkan Ürünler' in response.data.decode('utf-8')
    
    def test_about_page(self, client):
        """Test about page"""
        response = client.get('/hakkimizda')
        assert response.status_code == 200
    
    def test_contact_page(self, client):
        """Test contact page"""
        response = client.get('/iletisim')
        assert response.status_code == 200
    
    def test_help_page(self, client):
        """Test help page"""
        response = client.get('/yardim')
        assert response.status_code == 200
    
    def test_search_functionality(self, client, app):
        """Test search functionality"""
        with app.app_context():
            response = client.get('/ara?q=Test')
            assert response.status_code == 200
            
            response = client.get('/ara?q=Product')
            assert response.status_code == 200

class TestProductRoutes:
    """Test product-related routes"""
    
    def test_products_index(self, client):
        """Test products listing page"""
        response = client.get('/urunler/')
        assert response.status_code == 200
    
    def test_product_detail(self, client, app):
        """Test product detail page"""
        with app.app_context():
            product = Product.query.first()
            response = client.get(f'/urunler/{product.id}')
            assert response.status_code == 200
            assert product.name.encode() in response.data
    
    def test_category_page(self, client, app):
        """Test category page"""
        with app.app_context():
            category = Category.query.first()
            response = client.get(f'/urunler/kategori/{category.id}')
            assert response.status_code == 200
    
    def test_product_review_addition(self, client, app):
        """Test adding product review"""
        with app.app_context():
            login_user(client)
            
            product = Product.query.first()
            response = client.post(f'/urunler/{product.id}/yorum-ekle', data={
                'rating': 5,
                'title': 'Great product!',
                'comment': 'This is a test review'
            }, follow_redirects=True)
            
            assert response.status_code == 200
            
            # Check if review was created
            review = Review.query.filter_by(product_id=product.id).first()
            assert review is not None
            assert review.rating == 5
    
    def test_quick_view_api(self, client, app):
        """Test product quick view API"""
        with app.app_context():
            product = Product.query.first()
            response = client.get(f'/urunler/api/hizli-bakis/{product.id}')
            assert response.status_code == 200
            
            json_data = response.get_json()
            assert json_data['name'] == product.name
            assert json_data['price'] == product.get_formatted_price()

class TestCartRoutes:
    """Test shopping cart routes"""
    
    def test_cart_access_requires_login(self, client):
        """Test that cart requires authentication"""
        response = client.get('/sepet/')
        assert response.status_code == 302  # Redirect to login
    
    def test_cart_page_with_login(self, client, app):
        """Test cart page with authenticated user"""
        with app.app_context():
            login_user(client)
            response = client.get('/sepet/')
            assert response.status_code == 200
    
    def test_add_to_cart(self, client, app):
        """Test adding product to cart"""
        with app.app_context():
            login_user(client)
            
            product = Product.query.first()
            response = client.post(f'/sepet/ekle/{product.id}', data={
                'quantity': 2
            }, follow_redirects=True)
            
            assert response.status_code == 200
            
            # Check if cart item was created
            user = User.query.filter_by(username='testuser').first()
            cart_item = CartItem.query.filter_by(
                user_id=user.id, 
                product_id=product.id
            ).first()
            assert cart_item is not None
            assert cart_item.quantity == 2
    
    def test_cart_update(self, client, app):
        """Test updating cart item quantity"""
        with app.app_context():
            login_user(client)
            user = User.query.filter_by(username='testuser').first()
            product = Product.query.first()
            
            # First add item to cart
            cart_item = CartItem(
                user_id=user.id,
                product_id=product.id,
                quantity=1
            )
            db.session.add(cart_item)
            db.session.commit()
            
            # Update quantity
            response = client.post(f'/sepet/guncelle/{cart_item.id}', data={
                'quantity': 3
            }, follow_redirects=True)
            
            assert response.status_code == 200
            
            updated_item = CartItem.query.get(cart_item.id)
            assert updated_item.quantity == 3
    
    def test_checkout_process(self, client, app):
        """Test checkout process"""
        with app.app_context():
            login_user(client)
            user = User.query.filter_by(username='testuser').first()
            product = Product.query.first()
            
            # Add item to cart first
            cart_item = CartItem(
                user_id=user.id,
                product_id=product.id,
                quantity=1
            )
            db.session.add(cart_item)
            db.session.commit()
            
            # Test checkout page
            response = client.get('/sepet/odeme')
            assert response.status_code == 200
            
            # Test placing order
            response = client.post('/sepet/siparis-ver', data={
                'shipping_address': 'Test Address, Test City',
                'payment_method': 'Kredi Kartı',
                'notes': 'Test order'
            }, follow_redirects=True)
            
            assert response.status_code == 200
            
            # Check if order was created
            order = Order.query.filter_by(user_id=user.id).first()
            assert order is not None
            assert order.shipping_address == 'Test Address, Test City'

class TestAdminRoutes:
    """Test admin panel routes"""
    
    def test_admin_access_requires_admin_user(self, client):
        """Test that admin panel requires admin privileges"""
        login_user(client)  # Login as regular user
        response = client.get('/admin/')
        assert response.status_code == 302  # Redirect due to insufficient privileges
    
    def test_admin_dashboard(self, client, app):
        """Test admin dashboard access"""
        with app.app_context():
            login_admin(client)
            response = client.get('/admin/')
            assert response.status_code == 200
            assert b'Dashboard' in response.data or b'admin' in response.data.lower()
    
    def test_admin_products_page(self, client, app):
        """Test admin products management page"""
        with app.app_context():
            login_admin(client)
            response = client.get('/admin/urunler')
            assert response.status_code == 200
    
    def test_admin_orders_page(self, client, app):
        """Test admin orders management page"""
        with app.app_context():
            login_admin(client)
            response = client.get('/admin/siparisler')
            assert response.status_code == 200
    
    def test_admin_add_product(self, client, app):
        """Test adding product through admin panel"""
        with app.app_context():
            login_admin(client)
            
            category = Category.query.first()
            response = client.post('/admin/urunler/ekle', data={
                'name': 'New Test Product',
                'description': 'A new test product',
                'price': 500.0,
                'stock_quantity': 5,
                'category_id': category.id,
                'brand': 'TestBrand'
            }, follow_redirects=True)
            
            assert response.status_code == 200
            
            # Check if product was created
            product = Product.query.filter_by(name='New Test Product').first()
            assert product is not None
            assert product.price == 500.0

class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_404_error(self, client):
        """Test 404 error handling"""
        response = client.get('/nonexistent-page')
        assert response.status_code == 404
    
    def test_invalid_product_id(self, client):
        """Test accessing invalid product ID"""
        response = client.get('/urunler/99999')
        assert response.status_code == 404
    
    def test_add_to_cart_out_of_stock(self, client, app):
        """Test adding out of stock product to cart"""
        with app.app_context():
            login_user(client)
            
            # Create out of stock product
            category = Category.query.first()
            out_of_stock_product = Product(
                name='Out of Stock Product',
                price=100.0,
                stock_quantity=0,  # Out of stock
                category_id=category.id
            )
            db.session.add(out_of_stock_product)
            db.session.commit()
            
            response = client.post(f'/sepet/ekle/{out_of_stock_product.id}', data={
                'quantity': 1
            }, follow_redirects=True)
            
            assert response.status_code == 200
            assert 'stokta yok' in response.data.decode('utf-8').lower()
    
    def test_cart_api_count(self, client, app):
        """Test cart count API"""
        with app.app_context():
            login_user(client)
            
            response = client.get('/sepet/api/sepet-sayisi')
            assert response.status_code == 200
            
            json_data = response.get_json()
            assert 'count' in json_data
            assert isinstance(json_data['count'], int)

class TestFormValidation:
    """Test form validation"""
    
    def test_registration_form_validation(self, client):
        """Test registration form validation"""
        # Test empty form
        response = client.post('/auth/kayit', data={})
        assert response.status_code == 200
        
        # Test password mismatch
        response = client.post('/auth/kayit', data={
            'username': 'testuser2',
            'email': 'test2@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'password123',
            'password_confirm': 'different_password'
        })
        assert response.status_code == 200
    
    def test_login_form_validation(self, client):
        """Test login form validation"""
        # Test empty form
        response = client.post('/auth/giris', data={})
        assert response.status_code == 200
        
        # Test invalid credentials
        response = client.post('/auth/giris', data={
            'username': 'nonexistent',
            'password': 'wrongpassword'
        })
        assert response.status_code == 200
        assert 'Hatalı' in response.data.decode('utf-8') or 'hatalı' in response.data.decode('utf-8')

if __name__ == '__main__':
    pytest.main([__file__, '-v'])