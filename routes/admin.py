#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Admin Rotaları
Yönetici paneli rotaları
"""

import os
import uuid
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from functools import wraps
from app import db
from models.user import User
from models.product import Product, Category
from models.order import Order, OrderItem
from models.review import Review
from forms.admin import ProductForm

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    """Admin yetkisi kontrolü"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Bu sayfaya erişim yetkiniz yok!', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    """Admin ana paneli"""
    # İstatistikler
    total_users = User.query.count()
    total_products = Product.query.count()
    total_orders = Order.query.count()
    total_reviews = Review.query.count()
    
    # Son siparişler
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    
    # Düşük stoklu ürünler
    low_stock_products = Product.query.filter(
        Product.stock_quantity <= 10,
        Product.is_active == True
    ).limit(5).all()
    
    # Son yorumlar
    recent_reviews = Review.query.order_by(Review.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_products=total_products,
                         total_orders=total_orders,
                         total_reviews=total_reviews,
                         recent_orders=recent_orders,
                         low_stock_products=low_stock_products,
                         recent_reviews=recent_reviews)

@admin_bp.route('/urunler')
@login_required
@admin_required
def products():
    """Ürün yönetimi"""
    page = request.args.get('sayfa', 1, type=int)
    search = request.args.get('arama', '')
    category_id = request.args.get('kategori', type=int)
    
    query = Product.query
    
    # Arama filtresi
    if search:
        query = query.filter(Product.name.contains(search))
    
    # Kategori filtresi
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    products = query.order_by(Product.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    categories = Category.query.all()
    
    return render_template('admin/products.html', 
                         products=products, 
                         categories=categories,
                         search=search,
                         current_category=category_id)

@admin_bp.route('/urunler/ekle', methods=['GET', 'POST'])
@login_required
@admin_required
def add_product():
    """Ürün ekleme"""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price', type=float)
        original_price = request.form.get('original_price', type=float)
        stock_quantity = request.form.get('stock_quantity', type=int)
        category_id = request.form.get('category_id', type=int)
        brand = request.form.get('brand')
        model = request.form.get('model')
        color = request.form.get('color')
        size = request.form.get('size')
        is_featured = 'is_featured' in request.form
        is_active = 'is_active' in request.form
        
        # Resim yükleme işlemi
        image_url = request.form.get('image_url')  # URL ile resim
        uploaded_file = request.files.get('product_image')  # Dosya yükleme
        
        if uploaded_file and uploaded_file.filename != '':
            # Dosya yükleme işlemi
            if uploaded_file.filename and allowed_file(uploaded_file.filename):
                filename = secure_filename(uploaded_file.filename)
                # Benzersiz dosya adı oluştur
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                file_path = os.path.join('static', 'uploads', unique_filename)
                
                # Dosyayı kaydet
                try:
                    uploaded_file.save(file_path)
                    image_url = f"/static/uploads/{unique_filename}"
                except Exception as e:
                    flash(f'Dosya yüklenirken hata oluştu: {str(e)}', 'error')
                    return render_template('admin/add_product.html', 
                                         categories=Category.query.all())
            else:
                flash('Geçersiz dosya formatı! Sadece JPG, PNG ve GIF dosyaları kabul edilir.', 'error')
                return render_template('admin/add_product.html', 
                                     categories=Category.query.all())
        
        if not all([name, price, stock_quantity, category_id]):
            flash('Gerekli alanları doldurunuz!', 'error')
            return render_template('admin/add_product.html', 
                                 categories=Category.query.all())
        
        product = Product(
            name=name,
            description=description,
            price=price,
            original_price=original_price,
            stock_quantity=stock_quantity,
            category_id=category_id,
            brand=brand,
            model=model,
            color=color,
            size=size,
            image_url=image_url,
            is_featured=is_featured,
            is_active=is_active
        )
        
        db.session.add(product)
        db.session.commit()
        
        flash('Ürün başarıyla eklendi!', 'success')
        return redirect(url_for('admin.products'))
    
    categories = Category.query.all()
    return render_template('admin/add_product.html', categories=categories)

def allowed_file(filename):
    """İzin verilen dosya uzantılarını kontrol eder"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@admin_bp.route('/urunler/<int:product_id>/duzenle', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_product(product_id):
    """Ürün düzenleme"""
    product = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.price = request.form.get('price', type=float)
        product.original_price = request.form.get('original_price', type=float)
        product.stock_quantity = request.form.get('stock_quantity', type=int)
        product.category_id = request.form.get('category_id', type=int)
        product.brand = request.form.get('brand')
        product.model = request.form.get('model')
        product.color = request.form.get('color')
        product.size = request.form.get('size')
        product.is_featured = 'is_featured' in request.form
        product.is_active = 'is_active' in request.form
        
        db.session.commit()
        flash('Ürün güncellendi!', 'success')
        return redirect(url_for('admin.products'))
    
    categories = Category.query.all()
    return render_template('admin/edit_product.html', 
                         product=product, 
                         categories=categories)

@admin_bp.route('/siparisler')
@login_required
@admin_required
def orders():
    """Sipariş yönetimi"""
    page = request.args.get('sayfa', 1, type=int)
    status = request.args.get('durum')
    
    query = Order.query
    
    if status:
        query = query.filter_by(status=status)
    
    orders = query.order_by(Order.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/orders.html', orders=orders, current_status=status)

@admin_bp.route('/siparisler/<int:order_id>/duzenle', methods=['POST'])
@login_required
@admin_required
def update_order_status(order_id):
    """Sipariş durumu güncelleme"""
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    
    if new_status in ['Beklemede', 'Onaylandı', 'Kargoda', 'Teslim Edildi', 'İptal']:
        order.status = new_status
        
        if new_status == 'Kargoda':
            from datetime import datetime
            order.shipped_at = datetime.utcnow()
        elif new_status == 'Teslim Edildi':
            from datetime import datetime
            order.delivered_at = datetime.utcnow()
        
        db.session.commit()
        flash('Sipariş durumu güncellendi!', 'success')
    else:
        flash('Geçersiz durum!', 'error')
    
    return redirect(url_for('admin.orders'))

@admin_bp.route('/yorumlar')
@login_required
@admin_required
def reviews():
    """Yorum yönetimi"""
    page = request.args.get('sayfa', 1, type=int)
    
    reviews = Review.query.order_by(Review.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/reviews.html', reviews=reviews)

@admin_bp.route('/yorumlar/<int:review_id>/onayla', methods=['POST'])
@login_required
@admin_required
def approve_review(review_id):
    """Yorum onaylama"""
    review = Review.query.get_or_404(review_id)
    review.is_approved = True
    db.session.commit()
    
    flash('Yorum onaylandı!', 'success')
    return redirect(url_for('admin.reviews'))

@admin_bp.route('/yorumlar/<int:review_id>/reddet', methods=['POST'])
@login_required
@admin_required
def reject_review(review_id):
    """Yorum reddetme"""
    review = Review.query.get_or_404(review_id)
    review.is_approved = False
    db.session.commit()
    
    flash('Yorum reddedildi!', 'warning')
    return redirect(url_for('admin.reviews'))

@admin_bp.route('/kullanicilar')
@login_required
@admin_required
def users():
    """Kullanıcı yönetimi"""
    page = request.args.get('sayfa', 1, type=int)
    
    users = User.query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/users.html', users=users)