#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ürün Modeli
Ürün verilerini yöneten SQLAlchemy modeli
"""

from datetime import datetime
from app import db

class Category(db.Model):
    """Kategori modeli"""
    
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # İlişkiler
    products = db.relationship('Product', backref='category', lazy=True)
    
    def __repr__(self):
        return f'<Category {self.name}>'

class Product(db.Model):
    """Ürün modeli"""
    
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    shipping_fee = db.Column(db.Float, nullable=False, default=14.99)
    commission_fee = db.Column(db.Float, nullable=False, default=5.0)
    tax_fee = db.Column(db.Float, nullable=False, default=20.0)
    original_price = db.Column(db.Float, nullable=True)  # İndirim öncesi fiyat
    stock_quantity = db.Column(db.Integer, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    brand = db.Column(db.String(100), nullable=True)
    model = db.Column(db.String(100), nullable=True)
    color = db.Column(db.String(50), nullable=True)
    size = db.Column(db.String(50), nullable=True)
    weight = db.Column(db.Float, nullable=True)
    dimensions = db.Column(db.String(100), nullable=True)
    image_url = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    rating = db.Column(db.Float, default=0.0)
    review_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    cart_items = db.relationship('CartItem', backref='product', lazy=True)
    order_items = db.relationship('OrderItem', backref='product', lazy=True)
    reviews = db.relationship('Review', backref='product', lazy=True)
    
    def get_discount_percentage(self):
        """İndirim yüzdesini hesaplar"""
        if self.original_price and self.original_price > self.price:
            return int(((self.original_price - self.price) / self.original_price) * 100)
        return 0

    def get_final_price(self):
        """Nihai satış fiyatını tüm ücretler dahil hesaplar."""
        # Bu fonksiyon, oyuncunun belirlediği fiyata (self.price) göre maliyetleri ekleyerek
        # müşterinin ödeyeceği son fiyatı hesaplar.
        # Oyuncunun kârı: self.price - (ürün maliyeti)
        # Müşteri fiyatı: self.price + vergiler + komisyon + kargo

        # Komisyon, ürün fiyatı üzerinden hesaplanır
        commission_amount = self.price * (self.commission_fee / 100.0)

        # Vergi, (ürün fiyatı + komisyon) üzerinden hesaplanır
        price_before_tax = self.price + commission_amount
        tax_amount = price_before_tax * (self.tax_fee / 100.0)

        # Nihai fiyat
        final_price = self.price + tax_amount + self.shipping_fee
        return final_price
    
    def is_in_stock(self):
        """Stokta olup olmadığını kontrol eder"""
        return self.stock_quantity > 0
    
    def get_rating_stars(self):
        """Yıldız puanını döndürür"""
        return int(self.rating)
    
    def get_formatted_price(self):
        """Formatlanmış fiyat döndürür"""
        return f"{self.price:,.2f} ₺"
    
    def get_formatted_original_price(self):
        """Formatlanmış orijinal fiyat döndürür"""
        if self.original_price:
            return f"{self.original_price:,.2f} ₺"
        return None
    
    def __repr__(self):
        return f'<Product {self.name}>'