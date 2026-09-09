from fastapi import APIRouter, Depends, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.order import Order
from app.models.payment import PaymentTransaction
from app.services.payment_service import mark_order_paid

router = APIRouter(prefix="/click", tags=["Click Webhook"])

# Click Error Codes
CLICK_SUCCESS = 0
CLICK_ERROR_SIGN_CHECK = -1
CLICK_ERROR_INVALID_AMOUNT = -2
CLICK_ERROR_ACTION_NOT_FOUND = -3
CLICK_ERROR_ALREADY_PAID = -4
CLICK_ERROR_USER_NOT_FOUND = -5
CLICK_ERROR_TRANSACTION_NOT_FOUND = -6
CLICK_ERROR_UPDATE_FAILED = -7

@router.post("/prepare")
async def click_prepare(
    click_trans_id: str = Form(...),
    service_id: str = Form(...),
    click_paydoc_id: str = Form(...),
    merchant_trans_id: str = Form(...),
    amount: float = Form(...),
    action: int = Form(...),
    error: int = Form(...),
    error_note: str = Form(""),
    sign_time: str = Form(""),
    sign_string: str = Form(""),
    db: AsyncSession = Depends(get_db)
):
    """Click Prepare so'rovi (action=0)"""
    try:
        order_id = int(merchant_trans_id)
    except ValueError:
        return {
            "click_trans_id": click_trans_id,
            "merchant_trans_id": merchant_trans_id,
            "merchant_prepare_id": None,
            "error": CLICK_ERROR_USER_NOT_FOUND,
            "error_note": "Invalid Order ID"
        }

    res = await db.execute(select(Order).where(Order.id == order_id))
    order = res.scalar_one_or_none()

    if not order:
        return {
            "click_trans_id": click_trans_id,
            "merchant_trans_id": merchant_trans_id,
            "merchant_prepare_id": None,
            "error": CLICK_ERROR_USER_NOT_FOUND,
            "error_note": "Order not found"
        }

    if float(order.total_amount) != float(amount):
        return {
            "click_trans_id": click_trans_id,
            "merchant_trans_id": merchant_trans_id,
            "merchant_prepare_id": None,
            "error": CLICK_ERROR_INVALID_AMOUNT,
            "error_note": "Incorrect amount"
        }

    # Tranzaksiya yaratish
    tx = PaymentTransaction(
        order_id=order.id,
        provider="click",
        amount=int(amount),
        click_trans_id=click_trans_id,
        click_paydoc_id=click_paydoc_id,
        merchant_trans_id=merchant_trans_id,
        status="kutilmoqda"
    )
    db.add(tx)
    await db.commit()
    await db.refresh(tx)

    return {
        "click_trans_id": click_trans_id,
        "merchant_trans_id": merchant_trans_id,
        "merchant_prepare_id": str(tx.id),
        "error": CLICK_SUCCESS,
        "error_note": "Success"
    }

@router.post("/complete")
async def click_complete(
    click_trans_id: str = Form(...),
    service_id: str = Form(...),
    click_paydoc_id: str = Form(...),
    merchant_trans_id: str = Form(...),
    merchant_prepare_id: str = Form(...),
    amount: float = Form(...),
    action: int = Form(...),
    error: int = Form(...),
    error_note: str = Form(""),
    sign_time: str = Form(""),
    sign_string: str = Form(""),
    db: AsyncSession = Depends(get_db)
):
    """Click Complete so'rovi (action=1)"""
    tx_id = int(merchant_prepare_id)
    res = await db.execute(select(PaymentTransaction).where(PaymentTransaction.id == tx_id))
    tx = res.scalar_one_or_none()

    if not tx:
        return {
            "click_trans_id": click_trans_id,
            "merchant_trans_id": merchant_trans_id,
            "merchant_confirm_id": None,
            "error": CLICK_ERROR_TRANSACTION_NOT_FOUND,
            "error_note": "Transaction not found"
        }

    if error < 0:
        tx.status = "bekor_qilindi"
        tx.error_message = error_note
        await db.commit()
        return {
            "click_trans_id": click_trans_id,
            "merchant_trans_id": merchant_trans_id,
            "merchant_confirm_id": str(tx.id),
            "error": error,
            "error_note": error_note
        }

    tx.status = "muvaffaqiyatli"
    tx.state = 2
    await db.commit()

    # Buyurtmani to'langan deb belgilash
    await mark_order_paid(db, tx.order_id, "click", click_trans_id, int(amount))

    return {
        "click_trans_id": click_trans_id,
        "merchant_trans_id": merchant_trans_id,
        "merchant_confirm_id": str(tx.id),
        "error": CLICK_SUCCESS,
        "error_note": "Success"
    }
