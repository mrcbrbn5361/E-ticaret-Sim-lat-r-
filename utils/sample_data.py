#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Örnek Veri Oluşturma Modülü
Veritabanını örnek verilerle doldurur
"""

from app import db
from models.user import User
from models.product import Product, Category
from models.review import Review

def create_sample_data():
    """Örnek verileri oluşturur"""
    
    # Kategoriler zaten varsa işlem yapma
    if Category.query.count() > 0:
        return
    
    # E-ticaret kategorileri oluştur
    categories_data = [
        {'name': 'Elektronik', 'description': 'Telefon, bilgisayar, televizyon ve diğer elektronik ürünler'},
        {'name': 'Giyim & Moda', 'description': 'Kadın, erkek ve çocuk giyim ürünleri'},
        {'name': 'Ev & Yaşam', 'description': 'Ev eşyaları, dekorasyon ve mutfak ürünleri'},
        {'name': 'Kitap & Kırtasiye', 'description': 'Kitaplar, dergiler ve kırtasiye malzemeleri'},
        {'name': 'Spor & Outdoor', 'description': 'Spor ekipmanları ve açık hava ürünleri'},
        {'name': 'Sağlık & Güzellik', 'description': 'Kozmetik, kişisel bakım ve sağlık ürünleri'},
        {'name': 'Oyuncak & Bebek', 'description': 'Çocuk oyuncakları ve bebek ürünleri'},
        {'name': 'Otomotiv', 'description': 'Araç aksesuarları ve otomotiv ürünleri'}
    ]
    
    categories = []
    for cat_data in categories_data:
        category = Category(**cat_data)
        db.session.add(category)
        categories.append(category)
    
    db.session.commit()
    
    # Admin kullanıcı oluştur
    admin = User(
        username='admin',
        email='admin@gamestore.com',
        first_name='Admin',
        last_name='User',
        is_admin=True
    )
    admin.set_password('admin123')
    db.session.add(admin)
    
    db.session.commit()
    
    # Hiç ürün ekleme - kullanıcılar ekleyecek
    
    db.session.commit()
    
    print("E-ticaret simülâtör veri yapısı oluşturuldu!")
    print(f"- {len(categories)} e-ticaret kategorisi")
    print(f"- 0 ürün (kullanıcılar ekleyecek)")
    print(f"- 1 admin kullanıcı")
    print(f"- Ürünler yönetici panelinden eklenebilir")