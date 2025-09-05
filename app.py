#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E-Ticaret Simülatörü - Ana Uygulama Modülü
Flask uygulama fabrikası ve yapılandırması
"""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv

# Veritabanı nesnesi
db = SQLAlchemy()
# Giriş yöneticisi
login_manager = LoginManager()

def create_app():
    """Flask uygulaması oluşturur ve yapılandırır"""
    
    # .env dosyasını yükle
    load_dotenv()
    
    # Flask uygulaması oluştur
    app = Flask(__name__)
    
    # Uygulama yapılandırması
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'gizli-anahtar-eticaret-sim')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///eticaret.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['WTF_CSRF_ENABLED'] = True
    
    # Uzantıları başlat
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.giris'  # type: ignore
    login_manager.login_message = 'Bu sayfaya erişmek için lütfen giriş yapın.'
    login_manager.login_message_category = 'info'
    
    # Kullanıcı yükleyici
    from models.user import User
    from models.store import Store
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Blueprint'leri kaydet
    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.products import products_bp
    from routes.cart import cart_bp
    from routes.admin import admin_bp
    from routes.store import store_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(products_bp, url_prefix='/urunler')
    app.register_blueprint(cart_bp, url_prefix='/sepet')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(store_bp)
    
    # Veritabanı tablolarını oluştur
    with app.app_context():
        db.create_all()
        
        # Örnek veriler ekle
        from utils.sample_data import create_sample_data
        create_sample_data()
    
    return app