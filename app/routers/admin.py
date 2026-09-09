from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, delete
from sqlalchemy.orm import selectinload
from pathlib import Path
import re

from app.database import get_db
from app.models.product import Product, Category
from app.models.order import Order, OrderItem
from app.models.promo import PromoCode
from app.config import settings

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

router = APIRouter(prefix="/admin", tags=["Admin Panel"])

def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    return re.sub(r'[\s-]+', '-', text).strip('-')

# 1. Dashboard
@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
async def admin_dashboard(request: Request, db: AsyncSession = Depends(get_db)):
    # Total revenue
    rev_res = await db.execute(select(func.sum(Order.total_amount)).where(Order.payment_status == "tolandi"))
    total_revenue = rev_res.scalar() or 0

    # Total orders
    orders_res = await db.execute(select(func.count(Order.id)))
    total_orders = orders_res.scalar() or 0

    # Pending orders
    pending_res = await db.execute(select(func.count(Order.id)).where(Order.status.in_(["yangi", "qabul_qilindi", "tayyorlanmoqda"])))
    pending_orders_count = pending_res.scalar() or 0

    # Total products
    prod_res = await db.execute(select(func.count(Product.id)))
    total_products = prod_res.scalar() or 0

    # Low stock
    low_res = await db.execute(select(Product).where(Product.stock < 5))
    low_stock_products = low_res.scalars().all()

    # Recent orders
    recent_res = await db.execute(select(Order).order_by(Order.created_at.desc()).limit(8))
    recent_orders = recent_res.scalars().all()

    return templates.TemplateResponse(
        request=request,
        name="admin/dashboard.html",
        context={
            "active_page": "dashboard",
            "total_revenue": total_revenue,
            "total_orders": total_orders,
            "pending_orders_count": pending_orders_count,
            "total_products": total_products,
            "low_stock_products": low_stock_products,
            "recent_orders": recent_orders
        }
    )

# 2. Products List
@router.get("/products", response_class=HTMLResponse)
async def admin_products_list(request: Request, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Product).order_by(Product.id.desc()))
    products = res.scalars().all()
    return templates.TemplateResponse(
        request=request,
        name="admin/products.html",
        context={
            "active_page": "products",
            "products": products
        }
    )

# 3. New Product (GET & POST)
@router.get("/products/new", response_class=HTMLResponse)
async def admin_product_new_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="admin/product_form.html",
        context={
            "active_page": "products",
            "product": None
        }
    )

@router.post("/products/new")
async def admin_product_create(
    title: str = Form(...),
    artist: str = Form(...),
    genre: str = Form(...),
    release_year: int = Form(1995),
    condition: str = Form("Original Vintage"),
    tape_type: str = Form("Type I (Normal)"),
    duration_minutes: int = Form(60),
    label: str = Form("Tarona Records"),
    price: int = Form(...),
    old_price: int = Form(None),
    stock: int = Form(5),
    is_featured: bool = Form(False),
    is_new: bool = Form(True),
    image_url: str = Form(...),
    audio_sample_url: str = Form(None),
    audio_sample_title: str = Form(None),
    description: str = Form(None),
    tracklist_a: str = Form(None),
    tracklist_b: str = Form(None),
    db: AsyncSession = Depends(get_db)
):
    base_slug = slugify(f"{artist}-{title}")
    slug = base_slug
    idx = 1
    while True:
        check_res = await db.execute(select(Product).where(Product.slug == slug))
        if not check_res.scalar_one_or_none():
            break
        slug = f"{base_slug}-{idx}"
        idx += 1

    new_prod = Product(
        title=title,
        artist=artist,
        slug=slug,
        genre=genre,
        release_year=release_year,
        condition=condition,
        tape_type=tape_type,
        duration_minutes=duration_minutes,
        label=label,
        price=price,
        old_price=old_price,
        stock=stock,
        is_featured=is_featured,
        is_new=is_new,
        image_url=image_url,
        audio_sample_url=audio_sample_url,
        audio_sample_title=audio_sample_title,
        description=description,
        tracklist_a=tracklist_a,
        tracklist_b=tracklist_b
    )
    db.add(new_prod)
    await db.commit()
    return RedirectResponse(url="/admin/products", status_code=303)

# 4. Edit Product (GET & POST)
@router.get("/products/{id}/edit", response_class=HTMLResponse)
async def admin_product_edit_page(id: int, request: Request, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Product).where(Product.id == id))
    product = res.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Mahsulot topilmadi")
    return templates.TemplateResponse(
        request=request,
        name="admin/product_form.html",
        context={
            "active_page": "products",
            "product": product
        }
    )

@router.post("/products/{id}/edit")
async def admin_product_update(
    id: int,
    title: str = Form(...),
    artist: str = Form(...),
    genre: str = Form(...),
    release_year: int = Form(1995),
    condition: str = Form("Original Vintage"),
    tape_type: str = Form("Type I (Normal)"),
    duration_minutes: int = Form(60),
    label: str = Form("Tarona Records"),
    price: int = Form(...),
    old_price: int = Form(None),
    stock: int = Form(5),
    is_featured: bool = Form(False),
    is_new: bool = Form(True),
    image_url: str = Form(...),
    audio_sample_url: str = Form(None),
    audio_sample_title: str = Form(None),
    description: str = Form(None),
    tracklist_a: str = Form(None),
    tracklist_b: str = Form(None),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(select(Product).where(Product.id == id))
    product = res.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Mahsulot topilmadi")

    product.title = title
    product.artist = artist
    product.genre = genre
    product.release_year = release_year
    product.condition = condition
    product.tape_type = tape_type
    product.duration_minutes = duration_minutes
    product.label = label
    product.price = price
    product.old_price = old_price
    product.stock = stock
    product.is_featured = is_featured
    product.is_new = is_new
    product.image_url = image_url
    product.audio_sample_url = audio_sample_url
    product.audio_sample_title = audio_sample_title
    product.description = description
    product.tracklist_a = tracklist_a
    product.tracklist_b = tracklist_b

    await db.commit()
    return RedirectResponse(url="/admin/products", status_code=303)

# 5. Quick Stock Update
@router.post("/products/{id}/stock")
async def admin_quick_stock(id: int, request: Request, db: AsyncSession = Depends(get_db)):
    body = await request.json()
    delta = body.get("delta", 0)
    res = await db.execute(select(Product).where(Product.id == id))
    product = res.scalar_one_or_none()
    if product:
        product.stock = max(0, product.stock + delta)
        await db.commit()
    return {"success": True}

# 6. Delete Product
@router.post("/products/{id}/delete")
async def admin_delete_product(id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Product).where(Product.id == id))
    product = res.scalar_one_or_none()
    if product:
        await db.delete(product)
        await db.commit()
    return {"success": True}

# 7. Orders List
@router.get("/orders", response_class=HTMLResponse)
async def admin_orders_list(request: Request, status: str = None, db: AsyncSession = Depends(get_db)):
    stmt = select(Order).order_by(Order.created_at.desc())
    if status:
        stmt = stmt.where(Order.status == status)
    res = await db.execute(stmt)
    orders = res.scalars().all()
    return templates.TemplateResponse(
        request=request,
        name="admin/orders.html",
        context={
            "active_page": "orders",
            "orders": orders,
            "status_filter": status
        }
    )

# 8. Order Detail
@router.get("/orders/{id}", response_class=HTMLResponse)
async def admin_order_detail(id: int, request: Request, db: AsyncSession = Depends(get_db)):
    stmt = select(Order).where(Order.id == id).options(selectinload(Order.items))
    res = await db.execute(stmt)
    order = res.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Buyurtma topilmadi")
    return templates.TemplateResponse(
        request=request,
        name="admin/order_detail.html",
        context={
            "active_page": "orders",
            "order": order
        }
    )

# 9. Update Order
@router.post("/admin/orders/{id}/update")
@router.post("/orders/{id}/update")
async def admin_order_update_form(
    id: int,
    status: str = Form(...),
    payment_status: str = Form(...),
    courier_name: str = Form(None),
    courier_phone: str = Form(None),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Order).where(Order.id == id)
    res = await db.execute(stmt)
    order = res.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Buyurtma topilmadi")

    order.status = status
    order.payment_status = payment_status
    order.courier_name = courier_name
    order.courier_phone = courier_phone
    await db.commit()
    return RedirectResponse(url=f"/admin/orders/{id}", status_code=303)

@router.post("/orders/{id}/status")
async def admin_order_quick_status(id: int, request: Request, db: AsyncSession = Depends(get_db)):
    body = await request.json()
    new_status = body.get("status")
    stmt = select(Order).where(Order.id == id)
    res = await db.execute(stmt)
    order = res.scalar_one_or_none()
    if order and new_status:
        order.status = new_status
        await db.commit()
    return {"success": True}

# 10. Promo Codes
@router.get("/promos", response_class=HTMLResponse)
async def admin_promos_page(request: Request, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(PromoCode).order_by(PromoCode.created_at.desc()))
    promos = res.scalars().all()
    return templates.TemplateResponse(
        request=request,
        name="admin/promo_codes.html",
        context={
            "active_page": "promos",
            "promos": promos
        }
    )

@router.post("/promos/new")
async def admin_promo_create(
    code: str = Form(...),
    discount_type: str = Form("percent"),
    discount_value: int = Form(...),
    min_order_amount: int = Form(100000),
    max_uses: int = Form(100),
    description: str = Form(None),
    db: AsyncSession = Depends(get_db)
):
    promo = PromoCode(
        code=code.strip().upper(),
        discount_type=discount_type,
        discount_value=discount_value,
        min_order_amount=min_order_amount,
        max_uses=max_uses,
        description=description,
        is_active=True
    )
    db.add(promo)
    await db.commit()
    return RedirectResponse(url="/admin/promos", status_code=303)

@router.post("/promos/{id}/toggle")
async def admin_promo_toggle(id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(PromoCode).where(PromoCode.id == id))
    promo = res.scalar_one_or_none()
    if promo:
        promo.is_active = not promo.is_active
        await db.commit()
    return RedirectResponse(url="/admin/promos", status_code=303)

# 11. Settings
@router.get("/settings", response_class=HTMLResponse)
async def admin_settings_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="admin/settings.html",
        context={
            "active_page": "settings",
            "settings": settings
        }
    )

@router.post("/settings/save")
async def admin_settings_save(
    telegram_bot_token: str = Form(""),
    telegram_admin_chat_id: str = Form(""),
    delivery_tashkent_price: int = Form(25000),
    delivery_regions_price: int = Form(40000),
    free_delivery_threshold: int = Form(300000),
    payme_merchant_id: str = Form(""),
    payme_key: str = Form(""),
    click_service_id: str = Form(""),
    click_merchant_id: str = Form("")
):
    settings.TELEGRAM_BOT_TOKEN = telegram_bot_token
    settings.TELEGRAM_ADMIN_CHAT_ID = telegram_admin_chat_id
    settings.DELIVERY_TASHKENT_PRICE = delivery_tashkent_price
    settings.DELIVERY_REGIONS_PRICE = delivery_regions_price
    settings.FREE_DELIVERY_THRESHOLD = free_delivery_threshold
    settings.PAYME_MERCHANT_ID = payme_merchant_id
    settings.PAYME_KEY = payme_key
    settings.CLICK_SERVICE_ID = click_service_id
    settings.CLICK_MERCHANT_ID = click_merchant_id

    return RedirectResponse(url="/admin/settings", status_code=303)
