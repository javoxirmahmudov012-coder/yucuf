import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.product import Category, Product
from app.models.promo import PromoCode
from app.models.review import ProductReview

# ============================================================
#  UZRETRO.UZ — Haqiqiy Tarif Ro'yxati
#  Barcha narxlar 1 DONA KASSETA uchun amal qiladi
#  Aloqa: @uzretrouz | Admin: 87-770-02-33
# ============================================================

INITIAL_CATEGORIES = [
    {
        "name": "Start Tarif — 1 Kasseta",
        "slug": "tarif-start",
        "description": "Eng qulay narxda video kassetangizni fleshka yoki hard diskka ko'chirish. Fleshka yoki hard disk mijoz tomonidan beriladi.",
        "icon": "play"
    },
    {
        "name": "Standart Tarif — 1 Kasseta",
        "slug": "tarif-standart",
        "description": "Video kassetani tozalash (rang, yorqinlik, ovoz yaxshilash) + Fleshka/Hard disk + 8GB Fleshka BONUS + Yetkazib berish xizmati.",
        "icon": "star"
    },
    {
        "name": "PRO Tarif — 1 Kasseta",
        "slug": "tarif-pro",
        "description": "To'liq raqamlashtirish + Tozalash + 8GB Fleshka + QR kod + Shaxsiy YouTube havolasi + Olib ketish va yetkazib berish.",
        "icon": "zap"
    },
    {
        "name": "VIP Tarif — 1 Kasseta",
        "slug": "tarif-vip",
        "description": "Maksimal sifat: Tozalash + 16GB Fleshka + QR kod + YouTube + Duolar/Tabriklar alohida rolik + Olib ketish va yetkazib berish.",
        "icon": "crown"
    }
]

# 1 USD ≈ 12,700 UZS
# Start $20 = 254,000 so'm
# Standart $30 = 381,000 so'm
# PRO $50 = 635,000 so'm
# VIP $100 = 1,270,000 so'm

INITIAL_PRODUCTS = [
    # ─── START TARIF ─────────────────────────────────────────
    {
        "title": "Start Tarif — 1 Kasseta ($20)",
        "artist": "UZRETRO.UZ | @uzretrouz",
        "slug": "tarif-start-1-kasseta",
        "category_slug": "tarif-start",
        "genre": "Start Tarif — 1 Kasseta",
        "release_year": 2026,
        "condition": "Xizmat — Har 1 Kasseta Uchun",
        "tape_type": "VHS / VHS-C / MiniDV / Hi8 / Audio",
        "duration_minutes": 180,
        "country": "O'zbekiston / Toshkent",
        "label": "UZRETRO.UZ",
        "price": 254000,
        "old_price": 300000,
        "stock": 9999,
        "is_featured": True,
        "is_new": False,
        "image_url": "https://images.unsplash.com/photo-1544717305-2782549b5136?w=800&auto=format&fit=crop&q=80",
        "audio_sample_url": "https://cdn.freesound.org/previews/563/563821_12534887-lq.mp3",
        "audio_sample_title": "Video Raqamlashtirish Namunasi",
        "description": (
            "📼 HAR BIR KASSETA UCHUN $20 (≈254 000 so'm)\n\n"
            "✅ Video kassetadan fleshka, hard diskka ko'chirib berish\n"
            "✅ Fleshka yoki hard disk MIJOZ TOMONIDAN BERILADI\n\n"
            "📞 Buyurtma: @uzretrouz | Admin: 87-770-02-33\n"
            "Kuryer uyingizdan kassetangizni olib ketadi, tayyor bo'lgach qaytarib yetkazadi."
        ),
        "tracklist_a": "✅ Video kassetadan fleshka / hard diskka ko'chirish",
        "tracklist_b": "⚠️ Fleshka yoki hard disk MIJOZ tomonidan beriladi"
    },

    # ─── STANDART TARIF ──────────────────────────────────────
    {
        "title": "Standart Tarif — 1 Kasseta ($30)",
        "artist": "UZRETRO.UZ | @uzretrouz",
        "slug": "tarif-standart-1-kasseta",
        "category_slug": "tarif-standart",
        "genre": "Standart Tarif — 1 Kasseta",
        "release_year": 2026,
        "condition": "Xizmat — Har 1 Kasseta Uchun",
        "tape_type": "VHS / VHS-C / MiniDV / Hi8 / Audio",
        "duration_minutes": 180,
        "country": "O'zbekiston / Toshkent",
        "label": "UZRETRO.UZ",
        "price": 381000,
        "old_price": 450000,
        "stock": 9999,
        "is_featured": True,
        "is_new": False,
        "image_url": "https://images.unsplash.com/photo-1594623930572-300a3011d9ae?w=800&auto=format&fit=crop&q=80",
        "audio_sample_url": "https://cdn.freesound.org/previews/612/612613_5674468-lq.mp3",
        "audio_sample_title": "Rang va Ovoz Tiklash Namunasi",
        "description": (
            "📼 HAR BIR KASSETA UCHUN $30 (≈381 000 so'm)\n\n"
            "✅ Video kasseta avval tozalanadi:\n"
            "   — Video sifatini yaxshilash\n"
            "   — Rangni tiklash\n"
            "   — Yorqinlikni to'g'rilash\n"
            "   — Ovoz tozalash\n"
            "✅ Video kassetadan fleshka, hard diskka ko'chirib berish\n"
            "✅ 8 GB fleshka BONUS qilib yozib beriladi\n"
            "✅ Yetkazib berish xizmati (Yandex, BTS...)\n\n"
            "📞 Buyurtma: @uzretrouz | Admin: 87-770-02-33"
        ),
        "tracklist_a": (
            "✅ Video sifatini yaxshilash | Rang tiklash | Yorqinlik | Ovoz tozalash\n"
            "✅ Fleshka va Hard diskka ko'chirish"
        ),
        "tracklist_b": (
            "✅ 8 GB Fleshka BONUS yozib beriladi\n"
            "✅ Yetkazib berish xizmati (Yandex, BTS...)"
        )
    },

    # ─── PRO TARIF ───────────────────────────────────────────
    {
        "title": "PRO Tarif — 1 Kasseta ($50)",
        "artist": "UZRETRO.UZ | @uzretrouz",
        "slug": "tarif-pro-1-kasseta",
        "category_slug": "tarif-pro",
        "genre": "PRO Tarif — 1 Kasseta",
        "release_year": 2026,
        "condition": "Xizmat — Har 1 Kasseta Uchun",
        "tape_type": "VHS / VHS-C / MiniDV / Hi8 / Audio",
        "duration_minutes": 180,
        "country": "O'zbekiston / Toshkent",
        "label": "UZRETRO.UZ",
        "price": 635000,
        "old_price": 750000,
        "stock": 9999,
        "is_featured": True,
        "is_new": True,
        "image_url": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=800&auto=format&fit=crop&q=80",
        "audio_sample_url": "https://cdn.freesound.org/previews/450/450624_6142149-lq.mp3",
        "audio_sample_title": "PRO Sifat Namunasi",
        "description": (
            "📼 HAR BIR KASSETA UCHUN $50 (≈635 000 so'm)\n\n"
            "✅ Video kasseta avval tozalanadi:\n"
            "   — Video sifatini yaxshilash\n"
            "   — Rangni tiklash\n"
            "   — Yorqinlikni to'g'rilash\n"
            "   — Ovoz tozalash\n"
            "✅ Video kassetadan fleshka, hard diskka ko'chirib berish\n"
            "✅ 8 GB fleshka yozib beriladi\n"
            "✅ QR code beriladi\n"
            "✅ Shaxsiy yopiq YouTube link (istalgan vaqtda, istalgan joydan, istalgan qurilmadan ko'rish imkoniyati bor)\n"
            "✅ Olib ketish va yetkazib berish xizmati (Yandex, BTS...)\n\n"
            "📞 Buyurtma: @uzretrouz | Admin: 87-770-02-33"
        ),
        "tracklist_a": (
            "✅ Tozalash: Sifat, Rang, Yorqinlik, Ovoz\n"
            "✅ Fleshka & Hard disk | 8 GB Fleshka | QR code"
        ),
        "tracklist_b": (
            "✅ Shaxsiy yopiq YouTube link (har qurilmadan)\n"
            "✅ Olib ketish va yetkazib berish (Yandex, BTS...)"
        )
    },

    # ─── VIP TARIF ───────────────────────────────────────────
    {
        "title": "VIP Tarif — 1 Kasseta ($100)",
        "artist": "UZRETRO.UZ | @uzretrouz",
        "slug": "tarif-vip-1-kasseta",
        "category_slug": "tarif-vip",
        "genre": "VIP Tarif — 1 Kasseta",
        "release_year": 2026,
        "condition": "Xizmat — Har 1 Kasseta Uchun",
        "tape_type": "VHS / VHS-C / MiniDV / Hi8 / Audio",
        "duration_minutes": 180,
        "country": "O'zbekiston / Toshkent",
        "label": "UZRETRO.UZ",
        "price": 1270000,
        "old_price": 1500000,
        "stock": 9999,
        "is_featured": True,
        "is_new": True,
        "image_url": "https://images.unsplash.com/photo-1607604276583-eef5d076aa5f?w=800&auto=format&fit=crop&q=80",
        "audio_sample_url": "https://cdn.freesound.org/previews/612/612613_5674468-lq.mp3",
        "audio_sample_title": "VIP Premium Sifat Namunasi",
        "description": (
            "📼 HAR BIR KASSETA UCHUN $100 (≈1 270 000 so'm)\n\n"
            "✅ Video kasseta avval tozalanadi:\n"
            "   — Video sifatini yaxshilash\n"
            "   — Rangni tiklash\n"
            "   — Yorqinlikni to'g'rilash\n"
            "   — Ovoz tozalash\n"
            "✅ Video kassetadan fleshka, hard diskka ko'chirib berish\n"
            "✅ 16 GB fleshka yozib beriladi\n"
            "✅ QR code beriladi\n"
            "✅ Shaxsiy yopiq YouTube link (istalgan vaqtda, istalgan joydan, istalgan qurilmadan ko'rish imkoniyati bor)\n"
            "✅ Duolar, tabriklar, qadrli insonlar nutqi alohida rolik qilinadi\n"
            "   (Masalan: Qarindoshlar guruhi uchun 2-3 daqiqalik yoshi ulug' insonlarning o'sha paytdagi gaplari, duolari)\n"
            "✅ Olib ketish va yetkazib berish xizmati (Yandex, BTS...)\n\n"
            "📞 Buyurtma: @uzretrouz | Admin: 87-770-02-33"
        ),
        "tracklist_a": (
            "✅ Tozalash: Sifat, Rang, Yorqinlik, Ovoz\n"
            "✅ Fleshka & Hard disk | 16 GB Fleshka | QR code"
        ),
        "tracklist_b": (
            "✅ YouTube link | Duolar alohida rolik\n"
            "✅ Olib ketish va yetkazib berish (Yandex, BTS...)"
        )
    }
]

INITIAL_PROMOS = [
    {
        "code": "RETRO10",
        "description": "Barcha tariflar uchun 10% chegirma",
        "discount_type": "percent",
        "discount_value": 10,
        "min_order_amount": 250000,
        "max_uses": 500,
        "is_active": True
    },
    {
        "code": "UZRETRO",
        "description": "Instagram obunachilarimiz uchun 50 000 so'm chegirma",
        "discount_type": "fixed",
        "discount_value": 50000,
        "min_order_amount": 380000,
        "max_uses": 500,
        "is_active": True
    },
    {
        "code": "VIP2026",
        "description": "VIP tarif uchun 15% maxsus chegirma",
        "discount_type": "percent",
        "discount_value": 15,
        "min_order_amount": 1000000,
        "max_uses": 200,
        "is_active": True
    }
]

INITIAL_REVIEWS = [
    {
        "author_name": "Azizbek & Dilnoza",
        "author_city": "Toshkent",
        "rating": 5,
        "comment": "Ota-onamning 1996-yilgi to'y VHS kassetasini Standart tarifda topshirdik. Ranglar va ovoz shunchalik tiniq bo'libdiki, butun oilamiz yig'lab ko'rdik. 8GB fleshkaga ham yozib berishdi. Rahmat UZRETRO.UZ!",
        "is_verified_buyer": True
    },
    {
        "author_name": "Sardor Rahimov",
        "author_city": "Samarqand",
        "rating": 5,
        "comment": "PRO tarifni tanladim. QR kod va YouTube havola bilan butun qarindoshlarim telefonida ko'ra oldi. Kuryer uydan olib ketib, uyga olib keldi. Juda qulay xizmat!",
        "is_verified_buyer": True
    },
    {
        "author_name": "Nigora Alimova",
        "author_city": "Farg'ona",
        "rating": 5,
        "comment": "VIP tarif — duolar va tabriklar alohida rolik qilib berishdi. 87-770-02-33 ga qo'ng'iroq qilib buyurtma berdim, juda tez va professional xizmat ko'rsatishdi!",
        "is_verified_buyer": True
    }
]


async def seed_database(db: AsyncSession):
    # 1. Kategoriyalarni tekshirish va qo'shish / yangilash
    cat_map = {}
    for cat_data in INITIAL_CATEGORIES:
        stmt = select(Category).where(Category.slug == cat_data["slug"])
        res = await db.execute(stmt)
        cat = res.scalar_one_or_none()
        if not cat:
            cat = Category(
                name=cat_data["name"],
                slug=cat_data["slug"],
                description=cat_data["description"],
                icon=cat_data["icon"]
            )
            db.add(cat)
            await db.flush()
        else:
            cat.name = cat_data["name"]
            cat.description = cat_data["description"]
            cat.icon = cat_data["icon"]
            await db.flush()
        cat_map[cat.slug] = cat.id

    # 2. Mahsulotlarni tekshirish va qo'shish / yangilash
    for p_data in INITIAL_PRODUCTS:
        stmt = select(Product).where(Product.slug == p_data["slug"])
        res = await db.execute(stmt)
        product = res.scalar_one_or_none()
        cat_id = cat_map.get(p_data["category_slug"])
        if not product:
            product = Product(
                title=p_data["title"],
                artist=p_data["artist"],
                slug=p_data["slug"],
                category_id=cat_id,
                genre=p_data["genre"],
                release_year=p_data["release_year"],
                condition=p_data["condition"],
                tape_type=p_data["tape_type"],
                duration_minutes=p_data["duration_minutes"],
                country=p_data["country"],
                label=p_data["label"],
                price=p_data["price"],
                old_price=p_data["old_price"],
                stock=p_data["stock"],
                is_featured=p_data["is_featured"],
                is_new=p_data["is_new"],
                image_url=p_data["image_url"],
                audio_sample_url=p_data["audio_sample_url"],
                audio_sample_title=p_data["audio_sample_title"],
                description=p_data["description"],
                tracklist_a=p_data["tracklist_a"],
                tracklist_b=p_data["tracklist_b"]
            )
            db.add(product)
            await db.flush()
        else:
            product.title = p_data["title"]
            product.artist = p_data["artist"]
            product.category_id = cat_id
            product.genre = p_data["genre"]
            product.release_year = p_data["release_year"]
            product.condition = p_data["condition"]
            product.tape_type = p_data["tape_type"]
            product.duration_minutes = p_data["duration_minutes"]
            product.country = p_data["country"]
            product.label = p_data["label"]
            product.price = p_data["price"]
            product.old_price = p_data["old_price"]
            product.stock = p_data["stock"]
            product.is_featured = p_data["is_featured"]
            product.is_new = p_data["is_new"]
            product.image_url = p_data["image_url"]
            product.audio_sample_url = p_data["audio_sample_url"]
            product.audio_sample_title = p_data["audio_sample_title"]
            product.description = p_data["description"]
            product.tracklist_a = p_data["tracklist_a"]
            product.tracklist_b = p_data["tracklist_b"]
            await db.flush()

        # Boshlang'ich sharhlar — faqat birinchi mahsulotga
        if p_data["slug"] == "tarif-start-1-kasseta":
            rev_stmt = select(ProductReview).where(ProductReview.product_id == product.id)
            rev_res = await db.execute(rev_stmt)
            if not rev_res.scalars().all():
                for r_data in INITIAL_REVIEWS:
                    rev = ProductReview(
                        product_id=product.id,
                        author_name=r_data["author_name"],
                        author_city=r_data["author_city"],
                        rating=r_data["rating"],
                        comment=r_data["comment"],
                        is_verified_buyer=r_data["is_verified_buyer"],
                        is_approved=True
                    )
                    db.add(rev)

    # 3. Promokodlar
    for pr_data in INITIAL_PROMOS:
        stmt = select(PromoCode).where(PromoCode.code == pr_data["code"])
        res = await db.execute(stmt)
        promo = res.scalar_one_or_none()
        if not promo:
            promo = PromoCode(
                code=pr_data["code"],
                description=pr_data["description"],
                discount_type=pr_data["discount_type"],
                discount_value=pr_data["discount_value"],
                min_order_amount=pr_data["min_order_amount"],
                max_uses=pr_data["max_uses"],
                is_active=pr_data["is_active"]
            )
            db.add(promo)
        else:
            promo.description = pr_data["description"]
            promo.discount_type = pr_data["discount_type"]
            promo.discount_value = pr_data["discount_value"]
            promo.min_order_amount = pr_data["min_order_amount"]

    await db.commit()
