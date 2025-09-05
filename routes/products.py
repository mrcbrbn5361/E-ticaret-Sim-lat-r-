#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ürün Rotaları
Ürün listeleme, detay ve yönetim rotaları
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app import db
from models.product import Product, Category
from models.review import Review
from models.order import CartItem

products_bp = Blueprint('products', __name__)

@products_bp.route('/')
def index():
    """Tüm ürünler sayfası"""
    page = request.args.get('sayfa', 1, type=int)
    category_id = request.args.get('kategori', type=int)
    sort_by = request.args.get('sirala', 'name')
    
    # Temel sorgu
    query = Product.query.filter_by(is_active=True)
    
    # Kategori filtresi
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    # Sıralama
    if sort_by == 'price_asc':
        query = query.order_by(Product.price.asc())
    elif sort_by == 'price_desc':
        query = query.order_by(Product.price.desc())
    elif sort_by == 'rating':
        query = query.order_by(Product.rating.desc())
    elif sort_by == 'newest':
        query = query.order_by(Product.created_at.desc())
    else:
        query = query.order_by(Product.name.asc())
    
    # Sayfalama
    products = query.paginate(page=page, per_page=12, error_out=False)
    
    # Kategoriler
    categories = Category.query.filter_by(is_active=True).all()
    current_category = Category.query.get(category_id) if category_id else None
    
    return render_template('products/index.html', 
                         products=products,
                         categories=categories,
                         current_category=current_category,
                         current_sort=sort_by)

@products_bp.route('/kategori/<int:category_id>')
def category(category_id):
    """Kategori sayfası"""
    category = Category.query.get_or_404(category_id)
    page = request.args.get('sayfa', 1, type=int)
    sort_by = request.args.get('sirala', 'name')
    
    # Kategori ürünleri
    query = Product.query.filter_by(category_id=category_id, is_active=True)
    
    # Sıralama
    if sort_by == 'price_asc':
        query = query.order_by(Product.price.asc())
    elif sort_by == 'price_desc':
        query = query.order_by(Product.price.desc())
    elif sort_by == 'rating':
        query = query.order_by(Product.rating.desc())
    elif sort_by == 'newest':
        query = query.order_by(Product.created_at.desc())
    else:
        query = query.order_by(Product.name.asc())
    
    products = query.paginate(page=page, per_page=12, error_out=False)
    
    return render_template('products/category.html', 
                         category=category,
                         products=products,
                         current_sort=sort_by)

@products_bp.route('/<int:product_id>')
def detail(product_id):
    """Ürün detay sayfası"""
    product = Product.query.get_or_404(product_id)
    
    # Ürün yorumları
    reviews = Review.query.filter_by(
        product_id=product_id, 
        is_approved=True
    ).order_by(Review.created_at.desc()).limit(10).all()
    
    # Benzer ürünler
    similar_products = Product.query.filter(
        Product.category_id == product.category_id,
        Product.id != product_id,
        Product.is_active == True
    ).limit(4).all()
    
    # Kullanıcının sepetinde bu ürün var mı?
    in_cart = False
    cart_quantity = 0
    if current_user.is_authenticated:
        cart_item = CartItem.query.filter_by(
            user_id=current_user.id,
            product_id=product_id
        ).first()
        if cart_item:
            in_cart = True
            cart_quantity = cart_item.quantity
    
    return render_template('products/detail.html',
                         product=product,
                         reviews=reviews,
                         similar_products=similar_products,
                         in_cart=in_cart,
                         cart_quantity=cart_quantity)

@products_bp.route('/<int:product_id>/yorum-ekle', methods=['POST'])
@login_required
def add_review(product_id):
    """Ürün yorumu ekleme"""
    product = Product.query.get_or_404(product_id)
    
    # Kullanıcının daha önce yorum yapıp yapmadığını kontrol et
    existing_review = Review.query.filter_by(
        user_id=current_user.id,
        product_id=product_id
    ).first()
    
    if existing_review:
        flash('Bu ürün için zaten yorum yapmışsınız!', 'warning')
        return redirect(url_for('products.detail', product_id=product_id))
    
    rating = request.form.get('rating', type=int)
    title = request.form.get('title', '').strip()
    comment = request.form.get('comment', '').strip()
    
    if not rating or rating < 1 or rating > 5:
        flash('Geçerli bir puan seçiniz (1-5)!', 'error')
        return redirect(url_for('products.detail', product_id=product_id))
    
    # Yeni yorum oluştur
    review = Review(
        user_id=current_user.id,
        product_id=product_id,
        rating=rating,
        title=title,
        comment=comment
    )
    
    db.session.add(review)
    
    # Ürünün ortalama puanını güncelle
    all_reviews = Review.query.filter_by(product_id=product_id, is_approved=True).all()
    if all_reviews:
        total_rating = sum(r.rating for r in all_reviews) + rating
        product.rating = total_rating / (len(all_reviews) + 1)
        product.review_count = len(all_reviews) + 1
    else:
        product.rating = rating
        product.review_count = 1
    
    db.session.commit()
    flash('Yorumunuz başarıyla eklendi!', 'success')
    
    return redirect(url_for('products.detail', product_id=product_id))

@products_bp.route('/api/hizli-bakis/<int:product_id>')
def quick_view(product_id):
    """Ürün hızlı bakış (AJAX)"""
    product = Product.query.get_or_404(product_id)
    
    # Kullanıcının sepetinde bu ürün var mı?
    in_cart = False
    if current_user.is_authenticated:
        cart_item = CartItem.query.filter_by(
            user_id=current_user.id,
            product_id=product_id
        ).first()
        in_cart = bool(cart_item)
    
    return jsonify({
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.get_formatted_price(),
        'original_price': product.get_formatted_original_price(),
        'discount_percentage': product.get_discount_percentage(),
        'rating': product.rating,
        'review_count': product.review_count,
        'stock_quantity': product.stock_quantity,
        'in_stock': product.is_in_stock(),
        'in_cart': in_cart,
        'image_url': product.image_url or '/static/img/no-image.png',
        'brand': product.brand,
        'model': product.model,
        'color': product.color,
        'size': product.size
    })