#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sepet ve Sipariş Modelleri
Sepet ve sipariş verilerini yöneten SQLAlchemy modelleri
"""

from datetime import datetime
from app import db

class CartItem(db.Model):
    """Sepet öğesi modeli"""
    
    __tablename__ = 'cart_items'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_total_price(self):
        """Bu öğenin toplam fiyatını hesaplar"""
        return self.product.price * self.quantity
    
    def __repr__(self):
        return f'<CartItem {self.product.name} x{self.quantity}>'

class Order(db.Model):
    """Sipariş modeli"""
    
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(20), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='Beklemede')  # Beklemede, Onaylandı, Kargoda, Teslim Edildi, İptal
    total_amount = db.Column(db.Float, nullable=False)
    shipping_address = db.Column(db.Text, nullable=False)
    billing_address = db.Column(db.Text, nullable=True)
    payment_method = db.Column(db.String(50), nullable=False)
    payment_status = db.Column(db.String(20), default='Beklemede')  # Beklemede, Ödendi, İptal
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    shipped_at = db.Column(db.DateTime, nullable=True)
    delivered_at = db.Column(db.DateTime, nullable=True)
    
    # İlişkiler
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def get_status_badge_class(self):
        """Durum badge'i için CSS sınıfı döndürür"""
        status_classes = {
            'Beklemede': 'warning',
            'Onaylandı': 'info',
            'Kargoda': 'primary',
            'Teslim Edildi': 'success',
            'İptal': 'danger'
        }
        return status_classes.get(self.status, 'secondary')
    
    def get_formatted_total(self):
        """Formatlanmış toplam fiyat döndürür"""
        return f"{self.total_amount:,.2f} ₺"
    
    def get_item_count(self):
        """Siparişteki toplam ürün sayısını döndürür"""
        try:
            order_items = OrderItem.query.filter_by(order_id=self.id).all()
            return sum(item.quantity for item in order_items)
        except:
            return 0
    
    @staticmethod
    def generate_order_number():
        """Benzersiz sipariş numarası oluşturur"""
        import random
        import string
        timestamp = datetime.now().strftime('%Y%m%d')
        random_part = ''.join(random.choices(string.digits, k=4))
        return f"TR{timestamp}{random_part}"
    
    def __repr__(self):
        return f'<Order {self.order_number}>'

class OrderItem(db.Model):
    """Sipariş öğesi modeli"""
    
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)  # Sipariş anındaki fiyat
    total_price = db.Column(db.Float, nullable=False)
    
    def __repr__(self):
        return f'<OrderItem {self.product.name} x{self.quantity}>'