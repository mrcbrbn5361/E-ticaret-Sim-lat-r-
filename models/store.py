#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mağaza Modeli
Mağaza verilerini yöneten SQLAlchemy modeli
"""

from app import db

class Store(db.Model):
    """Represents a user's store in the game."""

    __tablename__ = 'stores'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    logo = db.Column(db.String(200), nullable=True)
    slogan = db.Column(db.String(250), nullable=True)
    category = db.Column(db.String(50), nullable=False)
    budget = db.Column(db.Float, nullable=False, default=15000.0)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    user = db.relationship('User', back_populates='store')

    def __repr__(self):
        return f'<Store {self.name}>'
