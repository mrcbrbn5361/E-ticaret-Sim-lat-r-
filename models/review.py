#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Değerlendirme Modeli
Ürün yorumları ve puanlamaları için SQLAlchemy modeli
"""

from datetime import datetime
from app import db

class Review(db.Model):
    """Ürün değerlendirmesi modeli"""
    
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 arası
    title = db.Column(db.String(200), nullable=True)
    comment = db.Column(db.Text, nullable=True)
    is_verified_purchase = db.Column(db.Boolean, default=False)
    is_approved = db.Column(db.Boolean, default=True)
    helpful_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_rating_stars(self):
        """Yıldız puanını döndürür"""
        return '★' * self.rating + '☆' * (5 - self.rating)
    
    def get_rating_percentage(self):
        """Puan yüzdesini döndürür"""
        return (self.rating / 5) * 100
    
    def get_short_comment(self, max_length=150):
        """Kısaltılmış yorum döndürür"""
        if self.comment and len(self.comment) > max_length:
            return self.comment[:max_length] + "..."
        return self.comment or ""
    
    @staticmethod
    def get_average_rating(product_id):
        """Belirli bir ürün için ortalama puanı hesaplar"""
        reviews = Review.query.filter_by(product_id=product_id, is_approved=True).all()
        if not reviews:
            return 0
        total_rating = sum(review.rating for review in reviews)
        return total_rating / len(reviews)
    
    def __repr__(self):
        return f'<Review {self.product.name} - {self.rating}/5>'