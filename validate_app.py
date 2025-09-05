#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Application Validation Script
Simple script to validate core application functionality
"""

import requests
import sys
from datetime import datetime

def test_endpoint(url, description):
    """Test a single endpoint"""
    try:
        response = requests.get(url, timeout=5)
        status = "✅ PASS" if response.status_code == 200 else f"❌ FAIL ({response.status_code})"
        print(f"{status} - {description}: {url}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ ERROR - {description}: {url} - {str(e)}")
        return False

def main():
    """Main validation function"""
    print("🧪 TrendyolApp E-Ticaret Simülatörü - Doğrulama Testi")
    print("=" * 60)
    print(f"Test Zamanı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    base_url = "http://localhost:5000"
    
    # Test endpoints
    tests = [
        (f"{base_url}/", "Ana Sayfa"),
        (f"{base_url}/urunler/", "Ürünler Sayfası"),
        (f"{base_url}/auth/giris", "Giriş Sayfası"),
        (f"{base_url}/auth/kayit", "Kayıt Sayfası"),
        (f"{base_url}/hakkimizda", "Hakkımızda Sayfası"),
        (f"{base_url}/iletisim", "İletişim Sayfası"),
        (f"{base_url}/ara", "Arama Sayfası"),
    ]
    
    passed = 0
    total = len(tests)
    
    print("🌐 Web Sayfaları Testi:")
    print("-" * 30)
    
    for url, description in tests:
        if test_endpoint(url, description):
            passed += 1
    
    print()
    print("📊 Test Sonuçları:")
    print("-" * 20)
    print(f"Geçen Testler: {passed}/{total}")
    print(f"Başarı Oranı: {(passed/total)*100:.1f}%")
    
    # Test specific content
    print()
    print("🔍 İçerik Doğrulama:")
    print("-" * 25)
    
    try:
        # Test homepage content
        response = requests.get(base_url)
        homepage_content = response.text
        
        content_tests = [
            ("TrendyolApp", "Site başlığı"),
            ("Kategoriler", "Kategoriler bölümü"),
            ("Öne Çıkan Ürünler", "Öne çıkan ürünler"),
            ("Elektronik", "Elektronik kategorisi"),
            ("Giyim", "Giyim kategorisi")
        ]
        
        content_passed = 0
        for content, description in content_tests:
            if content in homepage_content:
                print(f"✅ PASS - {description}: '{content}' bulundu")
                content_passed += 1
            else:
                print(f"❌ FAIL - {description}: '{content}' bulunamadı")
        
        print(f"\nİçerik Testleri: {content_passed}/{len(content_tests)}")
        
    except Exception as e:
        print(f"❌ İçerik testi hatası: {str(e)}")
    
    # Database validation
    print()
    print("🗄️ Veritabanı Doğrulama:")
    print("-" * 28)
    
    try:
        # Import app components to test database
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        from app import create_app, db
        from models.user import User
        from models.product import Product, Category
        
        app = create_app()
        with app.app_context():
            # Test database tables
            user_count = User.query.count()
            product_count = Product.query.count()
            category_count = Category.query.count()
            
            print(f"✅ Kullanıcılar: {user_count} kayıt")
            print(f"✅ Ürünler: {product_count} kayıt")
            print(f"✅ Kategoriler: {category_count} kayıt")
            
            # Test admin user
            admin = User.query.filter_by(is_admin=True).first()
            if admin:
                print(f"✅ Admin kullanıcı: {admin.username}")
            else:
                print("❌ Admin kullanıcı bulunamadı")
                
    except Exception as e:
        print(f"❌ Veritabanı testi hatası: {str(e)}")
    
    print()
    print("🎉 Doğrulama Tamamlandı!")
    
    if passed == total:
        print("✨ Tüm testler başarılı! Uygulama doğru çalışıyor.")
        return True
    else:
        print(f"⚠️ {total - passed} test başarısız. Lütfen kontrol edin.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)