import aiohttp
import logging
from app.config import settings

logger = logging.getLogger("telegram_service")

async def send_telegram_order_notification(order, items):
    """
    Yangi buyurtma tushganda Telegram bot orqali adminga chiroyli xabar yuborish.
    """
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_ADMIN_CHAT_ID:
        logger.info(f"Telegram sozlanmagan: Yangi buyurtma #{order.order_number} ({order.total_amount:,} so'm)")
        return False

    items_text = ""
    for idx, item in enumerate(items, 1):
        items_text += f"{idx}. 📼 <b>{item.product_title}</b> — {item.product_artist}\n"
        items_text += f"   └ {item.quantity} dona × {item.price:,} so'm = <b>{item.subtotal:,} so'm</b>\n"

    payment_method_labels = {
        "payme": "💳 Payme (Online)",
        "click": "🔵 Click (Online)",
        "cash": "💵 Kuryerga naqd / karta"
    }

    landmark_line = f"🏢 <b>Mo'ljal:</b> {order.landmark}\n" if order.landmark else ""
    notes_line = f"📝 <b>Izoh:</b> {order.delivery_notes}\n" if order.delivery_notes else ""
    discount_line = f"🏷 <b>Promokod chegirmasi:</b> -{order.discount_amount:,} so'm\n" if order.discount_amount else ""
    pay_status_text = "✅ TO'LANGAN" if order.payment_status == "tolandi" else "⏳ KUTILMOQDA"

    message = (
        f"🚨 <b>YANGI BUYURTMA #{order.order_number}</b>\n\n"
        f"👤 <b>Mijoz:</b> {order.customer_name}\n"
        f"📞 <b>Telefon:</b> <a href='tel:{order.customer_phone}'>{order.customer_phone}</a>\n"
        f"📍 <b>Manzil:</b> {order.region}, {order.address}\n"
        f"{landmark_line}"
        f"{notes_line}\n"
        f"📦 <b>Buyurtma tarkibi:</b>\n{items_text}\n"
        f"🚚 <b>Yetkazib berish:</b> {order.delivery_fee:,} so'm\n"
        f"{discount_line}"
        f"💰 <b>JAMI SUMMA:</b> <b>{order.total_amount:,} so'm</b>\n"
        f"💳 <b>To'lov turi:</b> {payment_method_labels.get(order.payment_method, order.payment_method)}\n"
        f"📊 <b>To'lov holati:</b> {pay_status_text}\n"
        f"🕒 <b>Vaqt:</b> {order.created_at.strftime('%d.%m.%Y %H:%M')}"
    )

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": settings.TELEGRAM_ADMIN_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=5) as response:
                if response.status == 200:
                    logger.info(f"Telegram bildirishnomasi muvaffaqiyatli yuborildi: #{order.order_number}")
                    return True
                else:
                    res_text = await response.text()
                    logger.error(f"Telegram API xatosi: {res_text}")
    except Exception as e:
        logger.error(f"Telegramga xabar yuborishda xatolik: {e}")
    return False

async def send_telegram_payment_notification(order, payment_tx):
    """
    To'lov muvaffaqiyatli amalga oshganda Telegram botga xabar yuborish.
    """
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_ADMIN_CHAT_ID:
        return False

    message = (
        f"💰 <b>TO'LOV QABUL QILINDI!</b>\n\n"
        f"📦 <b>Buyurtma:</b> #{order.order_number}\n"
        f"👤 <b>Mijoz:</b> {order.customer_name} ({order.customer_phone})\n"
        f"💳 <b>Tizim:</b> {payment_tx.provider.upper()}\n"
        f"💵 <b>Summa:</b> <b>{payment_tx.amount:,} so'm</b>\n"
        f"🆔 <b>Tranzaksiya ID:</b> <code>{payment_tx.payme_transaction_id or payment_tx.click_trans_id or payment_tx.id}</code>\n"
        f"✅ Buyurtma holati 'Qabul qilindi'ga o'zgartirildi."
    )

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": settings.TELEGRAM_ADMIN_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=5) as response:
                return response.status == 200
    except Exception as e:
        logger.error(f"Telegram payment notification error: {e}")
        return False
