#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E-Ticaret Simülatörü - Ana Giriş Noktası
Türkçe E-Ticaret Simülasyonu Uygulaması

Bu dosya uygulamanın ana giriş noktasıdır.
"""

from app import create_app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)