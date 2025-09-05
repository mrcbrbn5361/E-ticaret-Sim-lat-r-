#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mağaza Formları
Mağaza oluşturma ve düzenleme için WTForms formları
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, URL

class CreateStoreForm(FlaskForm):
    """Mağaza oluşturma formu"""
    name = StringField(
        'Mağaza Adı',
        validators=[DataRequired(), Length(min=3, max=100)]
    )
    logo = StringField(
        'Logo URL',
        validators=[URL(), Length(max=200)]
    )
    slogan = StringField(
        'Slogan',
        validators=[Length(max=250)]
    )
    category = SelectField(
        'Satış Alanı',
        choices=[
            ('elektronik', 'Elektronik'),
            ('giyim', 'Giyim & Moda'),
            ('ev_yasam', 'Ev & Yaşam'),
            ('kitap', 'Kitap & Hobi'),
            ('kozmetik', 'Kozmetik & Kişisel Bakım')
        ],
        validators=[DataRequired()]
    )
    submit = SubmitField('Oyuna Başla')
