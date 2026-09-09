import base64
import hashlib
import time
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.models.order import Order
from app.models.payment import PaymentTransaction
from app.services.telegram_service import send_telegram_payment_notification

def generate_payme_link(order: Order) -> str:
    """
    Payme to'lov havolasini generatsiya qilish (summa tiyinda bo'ladi: 1 UZS = 100 tiyin).
    """
    amount_in_tiyin = int(order.total_amount * 100)
    params = f"m={settings.PAYME_MERCHANT_ID};ac.order_id={order.id};a={amount_in_tiyin}"
    encoded = base64.b64encode(params.encode("utf-8")).decode("utf-8")
    
    if settings.PAYME_TEST_MODE:
        return f"https://test.paycom.uz/{encoded}"
    return f"https://checkout.paycom.uz/{encoded}"

def generate_click_link(order: Order) -> str:
    """
    Click to'lov havolasini generatsiya qilish.
    """
    service_id = settings.CLICK_SERVICE_ID
    merchant_id = settings.CLICK_MERCHANT_ID
    amount = order.total_amount
    trans_param = order.id
    
    return (
        f"https://my.click.uz/services/pay"
        f"?service_id={service_id}"
        f"&merchant_id={merchant_id}"
        f"&amount={amount}"
        f"&transaction_param={trans_param}"
        f"&return_url={settings.SITE_URL}/payment/success/{order.id}"
    )

async def mark_order_paid(db: AsyncSession, order_id: int, provider: str, trans_id: str, amount: int):
    """
    Buyurtmani to'langan deb belgilash va Telegram botga xabar jo'natish.
    """
    stmt = select(Order).where(Order.id == order_id)
    res = await db.execute(stmt)
    order = res.scalar_one_or_none()
    
    if not order:
        return False
        
    order.payment_status = "tolandi"
    order.paid_at = datetime.utcnow()
    if order.status == "yangi":
        order.status = "qabul_qilindi"
        
    # Tranzaksiya yozuvini yaratish
    tx = PaymentTransaction(
        order_id=order.id,
        provider=provider,
        amount=amount,
        status="muvaffaqiyatli",
        payme_transaction_id=trans_id if provider == "payme" else None,
        click_trans_id=trans_id if provider == "click" else None,
        state=2
    )
    db.add(tx)
    await db.commit()
    await db.refresh(order)
    
    # Telegram xabarnomasi
    await send_telegram_payment_notification(order, tx)
    return True
