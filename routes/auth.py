#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kimlik Doğrulama Rotaları
Kullanıcı kaydı, girişi ve çıkışı rotaları
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.urls import url_parse
from datetime import datetime
from app import db
from models.user import User
from forms.auth import LoginForm, RegisterForm, EditProfileForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/giris', methods=['GET', 'POST'])
@auth_bp.route('/login', methods=['GET', 'POST'])
def giris():
    """Kullanıcı girişi"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and user.check_password(form.password.data):
            # Son giriş zamanını güncelle
            user.last_login = datetime.now()
            db.session.commit()
            
            login_user(user, remember=form.remember_me.data)
            flash('Başarıyla giriş yaptınız!', 'success')
            
            # Mağaza kontrolü ve yönlendirme
            if not user.store:
                flash('Oyuna başlamak için lütfen mağazanızı oluşturun.', 'info')
                return redirect(url_for('store.create_store'))

            # Sonraki sayfaya yönlendir
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('main.index')
            return redirect(next_page)
        else:
            flash('Hatalı kullanıcı adı veya şifre!', 'error')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/kayit', methods=['GET', 'POST'])
@auth_bp.route('/register', methods=['GET', 'POST'])
def kayit():
    """Kullanıcı kayıtı"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegisterForm()
    
    if form.validate_on_submit():
        try:
            # Kullanıcı adı kontrolü
            existing_user = User.query.filter_by(username=form.username.data).first()
            if existing_user:
                flash('Bu kullanıcı adı zaten kullanılıyor!', 'error')
                return render_template('auth/register.html', form=form)
            
            # Yeni kullanıcı oluştur
            user = User(
                username=form.username.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data
            )
            user.set_password(form.password.data)
            
            db.session.add(user)
            db.session.commit()
            
            flash('Kayıt işleminiz başarıyla tamamlandı! Şimdi giriş yapabilirsiniz.', 'success')
            return redirect(url_for('auth.giris'))
            
        except Exception as e:
            db.session.rollback()
            flash('Kayıt sırasında bir hata oluştu. Lütfen tekrar deneyin.', 'error')
            return render_template('auth/register.html', form=form)
    
    return render_template('auth/register.html', form=form)

# Registration removed - only admin can create users

@auth_bp.route('/cikis')
@login_required
def cikis():
    """Kullanıcı çıkışı"""
    logout_user()
    flash('Başarıyla çıkış yaptınız!', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/profil')
@login_required
def profile():
    """Kullanıcı profili"""
    # Son siparişler
    orders = current_user.orders.order_by(current_user.orders.created_at.desc()).limit(5).all()
    
    return render_template('auth/profile.html', orders=orders)

@auth_bp.route('/profil/duzenle', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Profil düzenleme"""
    form = EditProfileForm()
    
    # Form verilerini mevcut kullanıcı bilgileriyle doldur
    if request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
    
    if form.validate_on_submit():
        # Şifre değişikliği kontrolü
        if form.new_password.data:
            if not form.current_password.data:
                flash('Yeni şifre belirlemek için mevcut şifrenizi girmelisiniz!', 'error')
                return render_template('auth/edit_profile.html', form=form)
            
            if not current_user.check_password(form.current_password.data):
                flash('Mevcut şifreniz yanlış!', 'error')
                return render_template('auth/edit_profile.html', form=form)
        
        # Kullanıcı bilgilerini güncelle
        if form.first_name.data:
            current_user.first_name = form.first_name.data
        if form.last_name.data:
            current_user.last_name = form.last_name.data
        
        # Şifre değişikliği
        if form.new_password.data:
            current_user.set_password(form.new_password.data)
        
        db.session.commit()
        flash('Profil bilgileriniz güncellendi!', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/edit_profile.html', form=form)

@auth_bp.route('/siparislerim')
@login_required
def siparislerim():
    """Kullanıcının siparişleri"""
    from models.order import Order
    page = request.args.get('sayfa', 1, type=int)
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template('auth/orders.html', orders=orders)

@auth_bp.route('/siparis/<int:order_id>/iptal', methods=['POST'])
@login_required
def cancel_order(order_id):
    """Sipariş iptal etme"""
    from models.order import Order
    
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first()
    if not order:
        return jsonify({'success': False, 'message': 'Sipariş bulunamadı'})
    
    if order.status != 'Beklemede':
        return jsonify({'success': False, 'message': 'Bu sipariş iptal edilemez'})
    
    try:
        order.status = 'İptal Edildi'
        db.session.commit()
        return jsonify({'success': True, 'message': 'Sipariş başarıyla iptal edildi'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Sipariş iptal edilirken bir hata oluştu'})