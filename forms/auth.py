#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kimlik Doğrulama Formları
Giriş, kayıt ve profil düzenleme formları
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, Optional

class LoginForm(FlaskForm):
    """Giriş formu"""
    username = StringField('Kullanıcı Adı', validators=[
        DataRequired(message='Bu alan zorunludur.')
    ])
    password = PasswordField('Şifre', validators=[
        DataRequired(message='Bu alan zorunludur.')
    ])
    remember_me = BooleanField('Beni Hatırla')
    submit = SubmitField('Giriş Yap')

class RegisterForm(FlaskForm):
    """Kayıt formu"""
    username = StringField('Kullanıcı Adı', validators=[
        DataRequired(message='Bu alan zorunludur.'),
        Length(min=3, max=20, message='Kullanıcı adı 3-20 karakter arasında olmalıdır.')
    ])
    first_name = StringField('Ad', validators=[
        DataRequired(message='Bu alan zorunludur.'),
        Length(max=50, message='Ad en fazla 50 karakter olabilir.')
    ])
    last_name = StringField('Soyad', validators=[
        DataRequired(message='Bu alan zorunludur.'),
        Length(max=50, message='Soyad en fazla 50 karakter olabilir.')
    ])
    password = PasswordField('Şifre', validators=[
        DataRequired(message='Bu alan zorunludur.'),
        Length(min=6, message='Şifre en az 6 karakter olmalıdır.')
    ])
    confirm_password = PasswordField('Şifre Tekrar', validators=[
        DataRequired(message='Bu alan zorunludur.'),
        EqualTo('password', message='Şifreler uyuşmuyor.')
    ])
    submit = SubmitField('Kayıt Ol')

class EditProfileForm(FlaskForm):
    """Profil düzenleme formu"""
    first_name = StringField('Ad', validators=[
        Optional(),
        Length(max=50, message='Ad en fazla 50 karakter olabilir.')
    ])
    last_name = StringField('Soyad', validators=[
        Optional(),
        Length(max=50, message='Soyad en fazla 50 karakter olabilir.')
    ])
    current_password = PasswordField('Mevcut Şifre', validators=[
        Optional()
    ])
    new_password = PasswordField('Yeni Şifre', validators=[
        Optional(),
        Length(min=6, message='Şifre en az 6 karakter olmalıdır.')
    ])
    confirm_password = PasswordField('Yeni Şifre Tekrar', validators=[
        Optional(),
        EqualTo('new_password', message='Şifreler uyuşmuyor.')
    ])
    submit = SubmitField('Güncelle')