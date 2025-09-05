#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Admin Formları
Yönetici paneli formları
"""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, IntegerField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length, Optional

class ProductForm(FlaskForm):
    """Ürün ekleme/düzenleme formu"""
    name = StringField('Oyun Adı', validators=[
        DataRequired(message='Bu alan zorunludur.'),
        Length(min=2, max=200, message='Oyun adı 2-200 karakter arası olmalıdır.')
    ])
    
    description = TextAreaField('Açıklama', validators=[
        Optional(),
        Length(max=2000, message='Açıklama en fazla 2000 karakter olabilir.')
    ])
    
    price = FloatField('Fiyat (TL)', validators=[
        DataRequired(message='Bu alan zorunludur.'),
        NumberRange(min=0.01, message='Fiyat 0\'dan büyük olmalıdır.')
    ])
    
    original_price = FloatField('Orijinal Fiyat (TL)', validators=[
        Optional(),
        NumberRange(min=0.01, message='Orijinal fiyat 0\'dan büyük olmalıdır.')
    ])
    
    stock_quantity = IntegerField('Stok Miktarı', validators=[
        DataRequired(message='Bu alan zorunludur.'),
        NumberRange(min=0, message='Stok miktarı 0 veya daha büyük olmalıdır.')
    ])
    
    category_id = SelectField('Kategori', validators=[
        DataRequired(message='Bu alan zorunludur.')
    ], coerce=int)
    
    brand = StringField('Geliştirici/Yayıncı', validators=[
        Optional(),
        Length(max=100, message='Geliştirici adı en fazla 100 karakter olabilir.')
    ])
    
    model = StringField('Platform/Sürüm', validators=[
        Optional(),
        Length(max=100, message='Platform bilgisi en fazla 100 karakter olabilir.')
    ])
    
    color = StringField('Tema/Tür', validators=[
        Optional(),
        Length(max=50, message='Tema bilgisi en fazla 50 karakter olabilir.')
    ])
    
    size = StringField('Boyut/Gereksinim', validators=[
        Optional(),
        Length(max=50, message='Boyut bilgisi en fazla 50 karakter olabilir.')
    ])
    
    image_url = StringField('Oyun Resmi URL', validators=[
        Optional(),
        Length(max=255, message='URL en fazla 255 karakter olabilir.')
    ])
    
    is_active = BooleanField('Aktif')
    is_featured = BooleanField('Öne Çıkan')
    
    submit = SubmitField('Kaydet')
    
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        # Kategoriler dinamik olarak yüklenecek
        from models.product import Category
        self.category_id.choices = [(c.id, c.name) for c in Category.query.filter_by(is_active=True).all()]