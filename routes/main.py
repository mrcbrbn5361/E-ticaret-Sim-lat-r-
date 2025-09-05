#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ana Sayfalar Rotaları
Ana sayfa ve genel navigasyon rotaları
"""

from flask import Blueprint, render_template, request
from models.product import Product, Category
from models.review import Review

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Ana sayfa"""
    # Öne çıkan ürünler
    featured_products = Product.query.filter_by(is_featured=True, is_active=True).limit(8).all()
    
    # En çok satılan ürünler (örnek için random)
    bestsellers = Product.query.filter_by(is_active=True).limit(6).all()
    
    # Kategoriler
    categories = Category.query.filter_by(is_active=True).all()
    
    # Son incelemeler
    recent_reviews = Review.query.filter_by(is_approved=True).order_by(Review.created_at.desc()).limit(5).all()
    
    return render_template('index.html', 
                         featured_products=featured_products,
                         bestsellers=bestsellers,
                         categories=categories,
                         recent_reviews=recent_reviews)

@main_bp.route('/hakkimizda')
def about():
    """Hakkımızda sayfası"""
    return render_template('about.html')

@main_bp.route('/iletisim')
def contact():
    """İletişim sayfası"""
    return render_template('contact.html')

@main_bp.route('/yardim')
def help():
    """Yardım sayfası"""
    return render_template('help.html')

@main_bp.route('/gizlilik')
def privacy():
    """Gizlilik politikası"""
    return render_template('privacy.html')

@main_bp.route('/kullanim-kosullari')
def terms():
    """Kullanım koşulları"""
    return render_template('terms.html')

@main_bp.route('/ara')
def search():
    """Ürün arama"""
    query = request.args.get('q', '')
    category_id = request.args.get('kategori', type=int)
    min_price = request.args.get('min_fiyat', type=float)
    max_price = request.args.get('max_fiyat', type=float)
    sort_by = request.args.get('sirala', 'name')
    
    # Temel sorgu
    products_query = Product.query.filter_by(is_active=True)
    
    # Arama filtresi
    if query:
        products_query = products_query.filter(
            Product.name.contains(query) | 
            Product.description.contains(query) |
            Product.brand.contains(query)
        )
    
    # Kategori filtresi
    if category_id:
        products_query = products_query.filter_by(category_id=category_id)
    
    # Fiyat filtresi
    if min_price:
        products_query = products_query.filter(Product.price >= min_price)
    if max_price:
        products_query = products_query.filter(Product.price <= max_price)
    
    # Sıralama
    if sort_by == 'price_asc':
        products_query = products_query.order_by(Product.price.asc())
    elif sort_by == 'price_desc':
        products_query = products_query.order_by(Product.price.desc())
    elif sort_by == 'rating':
        products_query = products_query.order_by(Product.rating.desc())
    elif sort_by == 'newest':
        products_query = products_query.order_by(Product.created_at.desc())
    else:
        products_query = products_query.order_by(Product.name.asc())
    
    # Sayfalama
    page = request.args.get('sayfa', 1, type=int)
    products = products_query.paginate(
        page=page, per_page=12, error_out=False
    )
    
    # Kategoriler (filtre için)
    categories = Category.query.filter_by(is_active=True).all()
    
    return render_template('search.html', 
                         products=products,
                         categories=categories,
                         query=query,
                         current_category=category_id,
                         current_sort=sort_by,
                         min_price=min_price,
                         max_price=max_price)