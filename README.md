# TrendyolApp - Türkçe E-Ticaret Simülatörü

Gerçekçi bir e-ticaret deneyimi sunan, Python Flask tabanlı Türkçe e-ticaret simülatörü. Bu proje, modern e-ticaret sitelerinin temel özelliklerini simüle eder ve kullanıcılara kapsamlı bir alışveriş deneyimi sağlar.

## 🎯 Proje Özellikleri

### 📦 Temel Özellikler
- **Ürün Yönetimi**: Kapsamlı ürün katalogu, kategoriler, arama ve filtreleme
- **Kullanıcı Sistemi**: Kayıt, giriş, profil yönetimi ve sipariş geçmişi
- **Sepet Yönetimi**: Ürün ekleme/çıkarma, miktar güncelleme
- **Sipariş Sistemi**: Sipariş verme, durum takibi ve yönetimi
- **Admin Paneli**: Ürün, sipariş ve kullanıcı yönetimi
- **Değerlendirme Sistemi**: Ürün yorumları ve puanlama

### 🛍️ Hedef Kitle
- **Yaş Grubu**: 18-65 yaş arası Türk tüketicileri
- **Teknik Seviye**: Tüm kullanıcı seviyeleri için uygun
- **Kullanım Amacı**: E-ticaret deneyimi, eğitim ve demo

### 📱 Ürün Kategorileri
- **Elektronik**: Telefon, bilgisayar, aksesuar
- **Giyim**: Kadın, erkek, çocuk giyim
- **Ev & Yaşam**: Mobilya, dekorasyon, mutfak
- **Kitap & Hobi**: Kitaplar, oyuncaklar
- **Spor & Outdoor**: Spor malzemeleri
- **Kozmetik**: Güzellik ve kişisel bakım
- **Anne & Bebek**: Anne ve bebek ürünleri
- **Otomobil**: Araç aksesuarları

### 💳 Ödeme Yöntemleri (Simülasyon)
- Kredi/Banka Kartı
- Havale/EFT
- Kapıda Ödeme
- Sanal Cüzdan

## 🚀 Kurulum ve Çalıştırma

### Gereksinimler
- Python 3.10 veya üzeri
- pip (Python paket yöneticisi)

### 1. Projeyi İndirin
```bash
git clone https://github.com/yourusername/trendyolapp.git
cd trendyolapp
```

### 2. Sanal Ortam Oluşturun
```bash
# Windows
python -m venv eticaret_env
eticaret_env\\Scripts\\activate

# macOS/Linux
python3 -m venv eticaret_env
source eticaret_env/bin/activate
```

### 3. Bağımlılıkları Yükleyin
```bash
pip install -r requirements.txt
```

### 4. Çevre Değişkenlerini Ayarlayın
`.env` dosyası zaten yapılandırılmıştır. Gerekirse düzenleyebilirsiniz:
```
SECRET_KEY=eticaret-sim-gizli-anahtar-2024
DATABASE_URL=sqlite:///eticaret.db
FLASK_ENV=development
FLASK_DEBUG=True
```

### 5. Uygulamayı Başlatın
```bash
python main.py
```

Uygulama `http://localhost:5000` adresinde çalışacaktır.

## 📁 Proje Yapısı

```
trendyolapp/
├── app.py                  # Flask uygulama fabrikası
├── main.py                 # Ana giriş noktası
├── requirements.txt        # Python bağımlılıkları
├── .env                    # Çevre değişkenleri
├── models/                 # Veritabanı modelleri
│   ├── user.py            # Kullanıcı modeli
│   ├── product.py         # Ürün ve kategori modeli
│   ├── order.py           # Sipariş ve sepet modeli
│   └── review.py          # Değerlendirme modeli
├── routes/                 # Flask Blueprint rotaları
│   ├── main.py            # Ana sayfa rotaları
│   ├── auth.py            # Kimlik doğrulama rotaları
│   ├── products.py        # Ürün rotaları
│   ├── cart.py            # Sepet rotaları
│   └── admin.py           # Admin rotaları
├── forms/                  # WTForms formları
│   └── auth.py            # Kimlik doğrulama formları
├── templates/              # HTML şablonları
│   ├── base.html          # Ana şablon
│   ├── index.html         # Ana sayfa
│   ├── auth/              # Kimlik doğrulama şablonları
│   ├── products/          # Ürün şablonları
│   ├── cart/              # Sepet şablonları
│   └── admin/             # Admin şablonları
├── static/                 # Statik dosyalar
│   └── img/               # Resimler
├── utils/                  # Yardımcı modüller
│   └── sample_data.py     # Örnek veri oluşturma
└── tests/                  # Test dosyaları
```

## 👤 Varsayılan Kullanıcılar

Uygulama ilk çalıştırıldığında otomatik olarak örnek kullanıcılar oluşturulur:

### Admin Kullanıcı
- **Kullanıcı Adı**: `admin`
- **Şifre**: `admin123`
- **E-posta**: `admin@eticaret.com`
- **Yetki**: Admin paneline erişim

### Normal Kullanıcı
- **Kullanıcı Adı**: `ahmet`
- **Şifre**: `123456`
- **E-posta**: `ahmet@example.com`
- **Yetki**: Standart kullanıcı

## 🔧 Kullanılan Teknolojiler

### Backend
- **Flask 2.3.3**: Web framework
- **SQLAlchemy 3.0.5**: ORM (Veritabanı)
- **Flask-Login 0.6.3**: Kullanıcı oturum yönetimi
- **Flask-WTF 1.1.1**: Form yönetimi
- **Werkzeug 2.3.7**: WSGI araçları
- **BCrypt 4.0.1**: Şifre hashleme

### Frontend
- **Bootstrap 5.3.0**: CSS framework
- **Bootstrap Icons**: İkon seti
- **Jinja2 3.1.2**: Template engine

### Veritabanı
- **SQLite**: Geliştirme ortamı için hafif veritabanı

### Geliştirme Araçları
- **Python-dotenv 1.0.0**: Çevre değişkeni yönetimi
- **Faker 19.12.0**: Test verisi oluşturma
- **Pytest 7.4.3**: Test framework

## 📊 Veritabanı Şeması

### Tablolar
- **users**: Kullanıcı bilgileri
- **categories**: Ürün kategorileri
- **products**: Ürün bilgileri
- **cart_items**: Sepet öğeleri
- **orders**: Siparişler
- **order_items**: Sipariş öğeleri
- **reviews**: Ürün değerlendirmeleri

## 🎨 Kullanıcı Arayüzü Tasarımı

### Tasarım Prensipleri
- **Modern ve Responsive**: Bootstrap 5 ile mobil uyumlu
- **Türkçe Yerelleştirme**: Tamamen Türkçe arayüz
- **Kullanıcı Dostu**: Sezgisel navigasyon ve kolay kullanım
- **Görsel Zenginlik**: İkonlar ve görsel geri bildirimler
- **Erişilebilirlik**: Tüm kullanıcılar için erişilebilir

### Renk Paleti
- **Ana Renk**: Turuncu (#ff6000) - Trendyol teması
- **İkincil Renk**: Gri tonları
- **Başarı**: Yeşil (#10b981)
- **Uyarı**: Sarı (#f59e0b)
- **Hata**: Kırmızı (#ef4444)

## 🔐 Güvenlik Özellikleri

- **Şifre Hashleme**: BCrypt ile güvenli şifre depolama
- **CSRF Koruması**: WTF-CSRF ile form koruması
- **Oturum Yönetimi**: Flask-Login ile güvenli oturum
- **SQL Injection Koruması**: SQLAlchemy ORM kullanımı
- **XSS Koruması**: Jinja2 template engine otomatik escape

## 📱 Ek Özellikler

### Değerlendirme Sistemi
- 5 yıldızlı puanlama sistemi
- Detaylı yorumlar
- Doğrulanmış alışveriş kontrolü
- Admin onay sistemi

### Arama ve Filtreleme
- Ürün adı, açıklama ve marka bazlı arama
- Kategori filtreleme
- Fiyat aralığı filtreleme
- Çoklu sıralama seçenekleri

### Sepet Yönetimi
- Gerçek zamanlı sepet güncellemesi
- Stok kontrolü
- Toplam fiyat hesaplama
- Kargo ücreti hesaplama (100 TL üzeri ücretsiz)

### Admin Paneli
- Dashboard ile genel istatistikler
- Ürün yönetimi (CRUD işlemleri)
- Sipariş durumu yönetimi
- Kullanıcı yönetimi
- Yorum onay sistemi

## 🧪 Test

Test dosyalarını çalıştırmak için:
```bash
pytest tests/ -v
```

## 🚀 Geliştirme Planı

### Gelecek Özellikler
- [ ] Ürün resmi yükleme sistemi
- [ ] Canlı sohbet desteği
- [ ] E-posta bildirimleri
- [ ] Mobil uygulama (React Native)
- [ ] API dokümantasyonu
- [ ] Çoklu dil desteği

### Performans İyileştirmeleri
- [ ] Redis önbellek sistemi
- [ ] Veritabanı optimizasyonu
- [ ] CDN entegrasyonu
- [ ] Lazy loading

## 🤝 Katkıda Bulunma

1. Projeyi fork edin
2. Feature branch oluşturun (`git checkout -b feature/AmazingFeature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some AmazingFeature'`)
4. Branch'inizi push edin (`git push origin feature/AmazingFeature`)
5. Pull Request açın

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 📞 İletişim

- **Proje Sahibi**: [Adınız]
- **E-posta**: [your.email@example.com]
- **GitHub**: [https://github.com/yourusername]

## 🙏 Teşekkürler

Bu proje aşağıdaki açık kaynak projeleri kullanmaktadır:
- Flask ve Flask ekosistemi
- Bootstrap ve Bootstrap Icons
- SQLAlchemy
- Diğer tüm bağımlılıklar

---

**Not**: Bu proje eğitim ve demo amaçlı olarak geliştirilmiştir. Gerçek e-ticaret operasyonları için ek güvenlik önlemleri ve özellikler gerekebilir.