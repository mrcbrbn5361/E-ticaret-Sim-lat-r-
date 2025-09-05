#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sepet Rotaları
Sepet yönetimi rotaları
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app import db
from models.product import Product
from models.order import CartItem, Order, OrderItem

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/')
@login_required
def index():
    """Sepet sayfası"""
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    
    # Toplam hesapla
    total = sum(item.get_total_price() for item in cart_items)
    
    return render_template('cart/index.html', cart_items=cart_items, total=total)

@cart_bp.route('/ekle/<int:product_id>', methods=['POST'])
@login_required
def add_item(product_id):
    """Sepete ürün ekleme"""
    product = Product.query.get_or_404(product_id)
    quantity = request.form.get('quantity', 1, type=int)
    
    if quantity < 1:
        flash('Geçersiz miktar!', 'error')
        return redirect(url_for('products.detail', product_id=product_id))
    
    if not product.is_in_stock():
        flash('Bu ürün stokta yok!', 'error')
        return redirect(url_for('products.detail', product_id=product_id))
    
    if quantity > product.stock_quantity:
        flash(f'Stokta sadece {product.stock_quantity} adet var!', 'error')
        return redirect(url_for('products.detail', product_id=product_id))
    
    # Sepette var mı kontrol et
    cart_item = CartItem.query.filter_by(
        user_id=current_user.id,
        product_id=product_id
    ).first()
    
    if cart_item:
        # Mevcut miktarı artır
        new_quantity = cart_item.quantity + quantity
        if new_quantity > product.stock_quantity:
            flash(f'Sepetinizde zaten {cart_item.quantity} adet var. Toplam {product.stock_quantity} adeti geçemez!', 'error')
            return redirect(url_for('products.detail', product_id=product_id))
        
        cart_item.quantity = new_quantity
        flash(f'Sepetteki {product.name} miktarı güncellendi!', 'success')
    else:
        # Yeni ürün ekle
        cart_item = CartItem(
            user_id=current_user.id,
            product_id=product_id,
            quantity=quantity
        )
        db.session.add(cart_item)
        flash(f'{product.name} sepete eklendi!', 'success')
    
    db.session.commit()
    
    # AJAX isteği ise JSON dön
    if request.is_json or request.headers.get('Content-Type') == 'application/json':
        return jsonify({
            'success': True,
            'message': 'Ürün sepete eklendi!',
            'cart_count': current_user.get_cart_item_count()
        })
    
    return redirect(url_for('products.detail', product_id=product_id))

@cart_bp.route('/guncelle/<int:item_id>', methods=['POST'])
@login_required
def update_item(item_id):
    """Sepet öğesi güncelleme"""
    cart_item = CartItem.query.filter_by(
        id=item_id,
        user_id=current_user.id
    ).first_or_404()
    
    quantity = request.form.get('quantity', type=int)
    
    if quantity is None or quantity < 1:
        flash('Geçersiz miktar!', 'error')
        return redirect(url_for('cart.index'))
    
    if quantity > cart_item.product.stock_quantity:
        flash(f'Stokta sadece {cart_item.product.stock_quantity} adet var!', 'error')
        return redirect(url_for('cart.index'))
    
    cart_item.quantity = quantity
    db.session.commit()
    
    flash('Sepet güncellendi!', 'success')
    return redirect(url_for('cart.index'))

@cart_bp.route('/sil/<int:item_id>', methods=['POST'])
@login_required
def remove_item(item_id):
    """Sepetten ürün silme"""
    cart_item = CartItem.query.filter_by(
        id=item_id,
        user_id=current_user.id
    ).first_or_404()
    
    product_name = cart_item.product.name
    
    db.session.delete(cart_item)
    db.session.commit()
    
    flash(f'{product_name} sepetten çıkarıldı!', 'info')
    return redirect(url_for('cart.index'))

@cart_bp.route('/temizle', methods=['POST'])
@login_required
def clear_cart():
    """Sepeti temizleme"""
    CartItem.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    
    flash('Sepet temizlendi!', 'info')
    return redirect(url_for('cart.index'))

@cart_bp.route('/odeme')
@login_required
def checkout():
    """Ödeme sayfası"""
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    
    if not cart_items:
        flash('Sepetiniz boş!', 'warning')
        return redirect(url_for('cart.index'))
    
    # Stok kontrolü
    for item in cart_items:
        if not item.product.is_in_stock():
            flash(f'{item.product.name} stokta yok!', 'error')
            return redirect(url_for('cart.index'))
        
        if item.quantity > item.product.stock_quantity:
            flash(f'{item.product.name} için yeterli stok yok!', 'error')
            return redirect(url_for('cart.index'))
    
    # Toplam hesapla
    total = sum(item.get_total_price() for item in cart_items)
    
    # Kargo ücreti (100 TL üzeri ücretsiz)
    shipping_cost = 0 if total >= 100 else 15
    grand_total = total + shipping_cost
    
    return render_template('cart/checkout.html', 
                         cart_items=cart_items,
                         total=total,
                         shipping_cost=shipping_cost,
                         grand_total=grand_total)

@cart_bp.route('/siparis-ver', methods=['POST'])
@login_required
def place_order():
    """Sipariş verme"""
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    
    if not cart_items:
        flash('Sepetiniz boş!', 'warning')
        return redirect(url_for('cart.index'))
    
    # Form verilerini al
    shipping_address = request.form.get('shipping_address', '').strip()
    payment_method = request.form.get('payment_method', '').strip()
    notes = request.form.get('notes', '').strip()
    
    if not shipping_address:
        flash('Teslimat adresi gereklidir!', 'error')
        return redirect(url_for('cart.checkout'))
    
    if not payment_method:
        flash('Ödeme yöntemi seçiniz!', 'error')
        return redirect(url_for('cart.checkout'))
    
    # Stok kontrolü
    for item in cart_items:
        if item.quantity > item.product.stock_quantity:
            flash(f'{item.product.name} için yeterli stok yok!', 'error')
            return redirect(url_for('cart.checkout'))
    
    # Toplam hesapla
    total = sum(item.get_total_price() for item in cart_items)
    shipping_cost = 0 if total >= 100 else 15
    grand_total = total + shipping_cost
    
    # Sipariş oluştur
    order = Order(
        order_number=Order.generate_order_number(),
        user_id=current_user.id,
        total_amount=grand_total,
        shipping_address=shipping_address,
        payment_method=payment_method,
        notes=notes
    )
    
    db.session.add(order)
    db.session.flush()  # ID'yi al
    
    # Sipariş öğelerini oluştur
    for item in cart_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=item.product.price,
            total_price=item.get_total_price()
        )
        db.session.add(order_item)
        
        # Stoktan düş
        item.product.stock_quantity -= item.quantity
    
    # Sepeti temizle
    CartItem.query.filter_by(user_id=current_user.id).delete()
    
    db.session.commit()
    
    flash(f'Siparişiniz alındı! Sipariş numaranız: {order.order_number}', 'success')
    return redirect(url_for('cart.order_success', order_id=order.id))

@cart_bp.route('/siparis-basarili/<int:order_id>')
@login_required
def order_success(order_id):
    """Sipariş başarılı sayfası"""
    order = Order.query.filter_by(
        id=order_id,
        user_id=current_user.id
    ).first_or_404()
    
    return render_template('cart/order_success.html', order=order)

@cart_bp.route('/api/sepet-sayisi')
@login_required
def cart_count():
    """Sepet öğe sayısı (AJAX)"""
    count = current_user.get_cart_item_count()
    return jsonify({'count': count})