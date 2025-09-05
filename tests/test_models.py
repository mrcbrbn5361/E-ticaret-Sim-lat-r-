#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
User Model and Authentication Tests
Test cases for user registration, login, and profile management
"""

import pytest
import os
import tempfile
from app import create_app, db
from models.user import User
from models.product import Product, Category
from models.order import CartItem, Order, OrderItem

@pytest.fixture
def app():
    """Create test application"""
    # Create temporary database file
    db_fd, db_path = tempfile.mkstemp()
    
    # Create test app with temporary database
    test_app = create_app()
    test_app.config['TESTING'] = True
    test_app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    test_app.config['WTF_CSRF_ENABLED'] = False
    
    with test_app.app_context():
        db.create_all()
        yield test_app
        
    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create test CLI runner"""
    return app.test_cli_runner()

@pytest.fixture
def sample_user(app):
    """Create sample user for testing"""
    with app.app_context():
        # Clear existing users first
        User.query.delete()
        db.session.commit()
        
        user = User(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        user.set_password('testpass123')
        
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def admin_user(app):
    """Create admin user for testing"""
    with app.app_context():
        admin = User(
            username='admin',
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            is_admin=True
        )
        admin.set_password('admin123')
        
        db.session.add(admin)
        db.session.commit()
        return admin

@pytest.fixture
def sample_category():
    """Create sample category"""
    category = Category(
        name='Elektronik',
        description='Test electronics category'
    )
    db.session.add(category)
    db.session.commit()
    return category

@pytest.fixture
def sample_product(sample_category):
    """Create sample product"""
    product = Product(
        name='Test iPhone',
        description='Test smartphone',
        price=5000.0,
        stock_quantity=10,
        category_id=sample_category.id,
        brand='Apple'
    )
    db.session.add(product)
    db.session.commit()
    return product

class TestUserModel:
    """Test User model functionality"""
    
    def test_password_hashing(self, app):
        """Test password hashing and verification"""
        with app.app_context():
            user = User(username='test', email='test@example.com', 
                       first_name='Test', last_name='User')
            user.set_password('test123')
            
            assert user.password_hash is not None
            assert user.check_password('test123') == True
            assert user.check_password('wrong') == False
    
    def test_user_creation(self, app):
        """Test user creation with valid data"""
        with app.app_context():
            user = User(
                username='newuser',
                email='new@example.com',
                first_name='New',
                last_name='User'
            )
            user.set_password('password123')
            
            db.session.add(user)
            db.session.commit()
            
            saved_user = User.query.filter_by(username='newuser').first()
            assert saved_user is not None
            assert saved_user.email == 'new@example.com'
            assert saved_user.get_full_name() == 'New User'
            assert saved_user.is_admin == False
            assert saved_user.is_active == True
    
    def test_user_methods(self, app, sample_user):
        """Test user helper methods"""
        with app.app_context():
            assert sample_user.get_full_name() == 'Test User'
            assert sample_user.get_cart_item_count() == 0
            assert sample_user.get_cart_total() == 0

class TestAuthentication:
    """Test authentication routes"""
    
    def test_register_page(self, client):
        """Test registration page access"""
        response = client.get('/auth/kayit')
        assert response.status_code == 200
        assert 'Kayıt Ol' in response.data.decode('utf-8')
    
    def test_login_page(self, client):
        """Test login page access"""
        response = client.get('/auth/giris')
        assert response.status_code == 200
        assert 'Giriş Yap' in response.data.decode('utf-8')
    
    def test_user_registration(self, client, app):
        """Test user registration process"""
        with app.app_context():
            response = client.post('/auth/kayit', data={
                'username': 'testuser2',
                'email': 'testuser2@example.com',
                'first_name': 'Test',
                'last_name': 'User2',
                'phone': '05551111111',
                'password': 'password123',
                'password_confirm': 'password123',
                'submit': 'Kayıt Ol'
            }, follow_redirects=True)
            
            assert response.status_code == 200
            
            # Check if user was created
            user = User.query.filter_by(username='testuser2').first()
            assert user is not None
            assert user.email == 'testuser2@example.com'
    
    def test_user_login(self, client, app, sample_user):
        """Test user login process"""
        with app.app_context():
            response = client.post('/auth/giris', data={
                'username': 'testuser',
                'password': 'testpass123',
                'submit': 'Giriş Yap'
            }, follow_redirects=True)
            
            assert response.status_code == 200
    
    def test_login_with_email(self, client, app, sample_user):
        """Test login with email instead of username"""
        with app.app_context():
            response = client.post('/auth/giris', data={
                'username': 'test@example.com',
                'password': 'testpass123',
                'submit': 'Giriş Yap'
            }, follow_redirects=True)
            
            assert response.status_code == 200
    
    def test_login_invalid_credentials(self, client, app, sample_user):
        """Test login with invalid credentials"""
        with app.app_context():
            response = client.post('/auth/giris', data={
                'username': 'testuser',
                'password': 'wrongpassword',
                'submit': 'Giriş Yap'
            })
            
            assert response.status_code == 200
            assert 'Hatalı kullanıcı adı veya şifre!' in response.data.decode('utf-8')

class TestProductModel:
    """Test Product model functionality"""
    
    def test_product_creation(self, app, sample_category):
        """Test product creation"""
        with app.app_context():
            product = Product(
                name='Test Product',
                description='A test product',
                price=100.0,
                original_price=120.0,
                stock_quantity=5,
                category_id=sample_category.id,
                brand='TestBrand'
            )
            
            db.session.add(product)
            db.session.commit()
            
            saved_product = Product.query.filter_by(name='Test Product').first()
            assert saved_product is not None
            assert saved_product.price == 100.0
            assert saved_product.is_in_stock() == True
            assert saved_product.get_discount_percentage() == 16  # (120-100)/120 * 100
    
    def test_product_methods(self, app, sample_product):
        """Test product helper methods"""
        with app.app_context():
            assert sample_product.is_in_stock() == True
            assert sample_product.get_formatted_price() == '5,000.00 ₺'
            
            # Test out of stock
            sample_product.stock_quantity = 0
            assert sample_product.is_in_stock() == False

class TestCartFunctionality:
    """Test shopping cart functionality"""
    
    def test_cart_item_creation(self, app, sample_user, sample_product):
        """Test adding items to cart"""
        with app.app_context():
            cart_item = CartItem(
                user_id=sample_user.id,
                product_id=sample_product.id,
                quantity=2
            )
            
            db.session.add(cart_item)
            db.session.commit()
            
            assert cart_item.get_total_price() == 10000.0  # 2 * 5000
            assert sample_user.get_cart_item_count() == 2
            assert sample_user.get_cart_total() == 10000.0
    
    def test_cart_routes(self, client, app, sample_user, sample_product):
        """Test cart-related routes"""
        with app.app_context():
            # Login first
            with client.session_transaction() as sess:
                sess['_user_id'] = str(sample_user.id)
                sess['_fresh'] = True
            
            # Test cart page
            response = client.get('/sepet/')
            assert response.status_code == 200
            
            # Test adding item to cart
            response = client.post(f'/sepet/ekle/{sample_product.id}', data={
                'quantity': 1
            }, follow_redirects=True)
            assert response.status_code == 200

class TestOrderFunctionality:
    """Test order creation and management"""
    
    def test_order_creation(self, app, sample_user, sample_product):
        """Test order creation"""
        with app.app_context():
            order = Order(
                order_number='TEST123456',
                user_id=sample_user.id,
                total_amount=5015.0,  # Product price + shipping
                shipping_address='Test Address',
                payment_method='Kredi Kartı'
            )
            
            db.session.add(order)
            db.session.flush()
            
            order_item = OrderItem(
                order_id=order.id,
                product_id=sample_product.id,
                quantity=1,
                unit_price=sample_product.price,
                total_price=sample_product.price
            )
            
            db.session.add(order_item)
            db.session.commit()
            
            assert order.get_formatted_total() == '5,015.00 ₺'
            assert order.get_item_count() == 1
            assert order.status == 'Beklemede'
    
    def test_order_number_generation(self, app):
        """Test order number generation"""
        with app.app_context():
            order_number = Order.generate_order_number()
            assert order_number.startswith('TR')
            assert len(order_number) == 14  # TR + 8 digit date + 4 random

if __name__ == '__main__':
    pytest.main([__file__, '-v'])