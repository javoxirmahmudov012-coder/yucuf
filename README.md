# UZRETRO.UZ 📼

> **Video & Audio Kassetalarni Fleshka, Hard disk va Cloudga O'tkazish Xizmati**
>
> Instagram: [@uzretrouz](https://instagram.com/uzretrouz) · Tel: 87-770-02-33

---

## Loyiha Haqida

**UZRETRO.UZ** — Toshkentdagi professional video va audio kasseta raqamlashtirish studiyasi. Sayt FastAPI + Jinja2 + Tailwind CSS asosida qurilgan.

**Asosiy imkoniyatlar:**
- 📋 4 ta xizmat tarifi (Start / Standart / PRO / VIP) — har 1 kasseta uchun
- 🛒 Savatcha va buyurtma tizimi
- 💳 Payme & Click to'lov integratsiyasi (webhook)
- 📦 Buyurtmani kuzatish sahifasi
- 🤖 Telegram bot xabarnomasi (yangi buyurtma va to'lov)
- 🛡️ Admin panel (buyurtmalar, mahsulotlar, promokodlar)

---

## Texnologiyalar

| Stack | Versiya |
|-------|---------|
| Python | 3.10+ |
| FastAPI | 0.110+ |
| SQLAlchemy (Async) | 2.0+ |
| Jinja2 | 3.1+ |
| Tailwind CSS | CDN |
| SQLite | (aiosqlite) |
| Payme / Click | Webhook |

---

## O'rnatish

### 1. Repozitoriyani klonlash

```bash
git clone https://github.com/sizning_username/uzretro-uz.git
cd uzretro-uz
```

### 2. Virtual muhit va kutubxonalar

```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux

pip install -r requirements.txt
```

### 3. `.env` faylini sozlash

```bash
cp .env.example .env
```

`.env` faylini oching va quyidagi qiymatlarni kiriting:

```env
SECRET_KEY=your_very_strong_random_secret_key
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_strong_password
SITE_URL=https://uzretro.uz

PAYME_MERCHANT_ID=...
PAYME_KEY=...

CLICK_SERVICE_ID=...
CLICK_MERCHANT_ID=...
CLICK_SECRET_KEY=...

TELEGRAM_BOT_TOKEN=...
TELEGRAM_ADMIN_CHAT_ID=...
```

### 4. Ishga tushirish

```bash
python run.py
```

Sayt: **http://127.0.0.1:8000**
Admin: **http://127.0.0.1:8000/admin**

---

## Loyiha Tuzilmasi

```
kassetalar_store/
├── app/
│   ├── config.py          # Sozlamalar (.env dan o'qiladi)
│   ├── database.py        # SQLAlchemy Async engine
│   ├── main.py            # FastAPI app, lifespan, router bağlantılari
│   ├── models/            # SQLAlchemy ORM modellari
│   │   ├── order.py
│   │   ├── payment.py
│   │   ├── product.py
│   │   ├── promo.py
│   │   └── review.py
│   ├── routers/           # API va sahifa router'lari
│   │   ├── admin.py       # Admin panel
│   │   ├── api.py         # REST API (buyurtma, promo, sharh)
│   │   ├── click_pay.py   # Click webhook
│   │   ├── payme.py       # Payme JSON-RPC webhook
│   │   └── store.py       # Ommaviy sahifalar (bosh sahifa, katalog, ...)
│   ├── schemas/
│   │   └── schemas.py     # Pydantic sxemalar
│   ├── services/
│   │   ├── order_service.py    # Buyurtma yaratish logikasi
│   │   ├── payment_service.py  # To'lov havolalari va mark_paid
│   │   ├── seed_data.py        # Boshlang'ich ma'lumotlar
│   │   └── telegram_service.py # Telegram bot xabarnomasi
│   ├── static/            # CSS, JS, rasmlar
│   └── templates/         # Jinja2 HTML shablonlar
├── .env.example           # Muhit o'zgaruvchilari namunasi
├── .gitignore
├── requirements.txt
├── run.py                 # Serverni ishga tushirish
└── README.md
```

---

## Xizmat Tariflari

| Tarif | Narx | Nima kiradi |
|-------|------|-------------|
| **Start** | $20 / kasseta | Ko'chirish — fleshka mijozda |
| **Standart** | $30 / kasseta | Tozalash + 8GB Fleshka + Yetkazib berish |
| **PRO** | $50 / kasseta | Tozalash + 8GB + QR + YouTube link + Olib ketish |
| **VIP** | $100 / kasseta | Tozalash + 16GB + QR + YouTube + Duolar alohida + Olib ketish |

> Barcha narxlar **1 dona kasseta** uchun amal qiladi.

---

## Aloqa

- 📸 Instagram: [@uzretrouz](https://instagram.com/uzretrouz)
- 📞 Telefon: **87-770-02-33**

---

## Litsenziya

MIT License — shaxsiy va tijorat loyihalarda erkin foydalanishingiz mumkin.
