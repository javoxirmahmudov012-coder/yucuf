from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.promo import PromoCode
from app.schemas.schemas import OrderCreateSchema
from app.config import settings
from app.services.telegram_service import send_telegram_order_notification

async def create_order_from_cart(db: AsyncSession, order_data: OrderCreateSchema) -> Order:
    # 1. Mahsulotlarni bazadan tekshirish va yig'ish
    product_ids = [item.product_id for item in order_data.items]
    stmt = select(Product).where(Product.id.in_(product_ids))
    res = await db.execute(stmt)
    products_map = {p.id: p for p in res.scalars().all()}
    
    items_total = 0
    order_items_to_create = []
    
    for item in order_data.items:
        product = products_map.get(item.product_id)
        if not product or not product.is_active:
            continue
            
        subtotal = product.price * item.quantity
        items_total += subtotal
        
        # Sklad qoldig'ini kamaytirish
        if product.stock >= item.quantity:
            product.stock -= item.quantity
        product.sales_count += item.quantity
        
        order_item = OrderItem(
            product_id=product.id,
            product_title=product.title,
            product_artist=product.artist,
            product_image=product.image_url,
            price=product.price,
            quantity=item.quantity,
            subtotal=subtotal
        )
        order_items_to_create.append(order_item)
        
    if not order_items_to_create:
        raise ValueError("Savatda faol mahsulotlar mavjud emas.")
        
    # 2. Yetkazib berish narxini aniqlash
    delivery_fee = settings.DELIVERY_TASHKENT_PRICE
    if order_data.region != "Toshkent shahri":
        delivery_fee = settings.DELIVERY_REGIONS_PRICE
    if order_data.delivery_method == "express":
        delivery_fee = settings.DELIVERY_EXPRESS_PRICE
        
    # Agar summa bepul yetkazib berish chegarasidan oshsa
    if items_total >= settings.FREE_DELIVERY_THRESHOLD:
        delivery_fee = 0
        
    # 3. Promokodni tekshirish va hisoblash
    discount_amount = 0
    applied_promo = None
    if order_data.promo_code:
        promo_stmt = select(PromoCode).where(PromoCode.code == order_data.promo_code.strip().upper())
        promo_res = await db.execute(promo_stmt)
        promo = promo_res.scalar_one_or_none()
        if promo and promo.is_active:
            discount_amount = promo.calculate_discount(items_total)
            if discount_amount > 0:
                applied_promo = promo.code
                promo.used_count += 1
                
    total_amount = max(0, items_total - discount_amount + delivery_fee)
    
    # 4. Yangi buyurtma yaratish
    new_order = Order(
        customer_name=order_data.customer_name,
        customer_phone=order_data.customer_phone,
        customer_email=order_data.customer_email,
        region=order_data.region,
        district=order_data.district,
        address=order_data.address,
        landmark=order_data.landmark,
        delivery_notes=order_data.delivery_notes,
        delivery_method=order_data.delivery_method,
        delivery_fee=delivery_fee,
        items_total=items_total,
        discount_amount=discount_amount,
        promo_code=applied_promo,
        total_amount=total_amount,
        payment_method=order_data.payment_method,
        payment_status="kutilmoqda",
        status="yangi"
    )
    
    new_order.items = order_items_to_create
    db.add(new_order)
    await db.commit()
    await db.refresh(new_order)
    
    # Telegram bot orqali bildirishnoma yuborish
    try:
        await send_telegram_order_notification(new_order, order_items_to_create)
    except Exception:
        pass
        
    return new_order
