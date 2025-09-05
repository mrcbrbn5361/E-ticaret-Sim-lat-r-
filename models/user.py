#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kullanıcı Modeli
Kullanıcı verilerini yöneten SQLAlchemy modeli
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(UserMixin, db.Model):
    """Simplified User model for gaming store"""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), nullable=True)  # Completely optional, no unique constraint
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=True, default='Player')
    last_name = db.Column(db.String(50), nullable=True, default='User')
    is_admin = db.Column(db.Boolean, default=False)
    active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    orders = db.relationship('Order', backref='customer', lazy=True)
    cart_items = db.relationship('CartItem', backref='user', lazy=True)
    
    def __init__(self, username=None, email=None, first_name=None, last_name=None, is_admin=False, **kwargs):
        """User constructor"""
        super().__init__(**kwargs)
        if username:
            self.username = username
        if email:
            self.email = email
        if first_name:
            self.first_name = first_name
        if last_name:
            self.last_name = last_name
        self.is_admin = is_admin
    
    @property
    def is_active(self):
        """Flask-Login için aktif durumu"""
        return self.active
    
    def set_password(self, password):
        """Şifreyi hashler ve kaydeder"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Şifreyi doğrular"""
        return check_password_hash(self.password_hash, password)
    
    def get_full_name(self):
        """Tam adı döndürür"""
        return f"{self.first_name} {self.last_name}"
    
    def get_cart_total(self):
        """Sepet toplam fiyatını hesaplar"""
        from models.order import CartItem
        total = 0
        try:
            cart_items = CartItem.query.filter_by(user_id=self.id).all()
            for item in cart_items:
                total += item.product.price * item.quantity
        except:
            pass
        return total
    
    def get_cart_item_count(self):
        """Sepetteki toplam ürün sayısını döndürür"""
        from models.order import CartItem
        total = 0
        try:
            cart_items = CartItem.query.filter_by(user_id=self.id).all()
            for item in cart_items:
                total += item.quantity
        except:
            pass
        return total
    
    def get_order_count(self):
        """Toplam sipariş sayısını döndürür"""
        from models.order import Order
        try:
            return Order.query.filter_by(user_id=self.id).count()
        except:
            return 0
    
    def get_total_spent(self):
        """Toplam harcama miktarını döndürür"""
        from models.order import Order
        total = 0
        try:
            orders = Order.query.filter_by(user_id=self.id).all()
            for order in orders:
                if order.status != 'İptal Edildi':
                    total += order.total_amount
        except:
            pass
        return total
    
    def get_review_count(self):
        """Satış odaklı oyun için basit metric döndürür"""
        try:
            # Basit bir satış metriği - sipariş başına ortalama
            return min(5, self.get_order_count())  # En fazla 5 göster
        except:
            return 0
    
    def __repr__(self):
        return f'<User {self.username}>'