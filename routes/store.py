#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mağaza Rotaları
Mağaza oluşturma ve yönetimi ile ilgili rotalar
"""

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from models.store import Store
from forms.store import CreateStoreForm

store_bp = Blueprint('store', __name__)

@store_bp.route('/magaza/olustur', methods=['GET', 'POST'])
@login_required
def create_store():
    """Yeni mağaza oluşturma"""
    # Kullanıcının zaten bir mağazası varsa, ana sayfaya yönlendir
    if current_user.store:
        return redirect(url_for('main.index'))

    form = CreateStoreForm()
    if form.validate_on_submit():
        new_store = Store(
            name=form.name.data,
            logo=form.logo.data,
            slogan=form.slogan.data,
            category=form.category.data,
            user_id=current_user.id
        )
        db.session.add(new_store)
        db.session.commit()

        flash('Mağazanız başarıyla oluşturuldu! Oyuna hoş geldiniz!', 'success')
        return redirect(url_for('main.index'))

    return render_template('store/create_store.html', form=form)
