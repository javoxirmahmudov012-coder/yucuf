import time
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.order import Order
from app.models.payment import PaymentTransaction
from app.services.payment_service import mark_order_paid

router = APIRouter(prefix="/payme", tags=["Payme Webhook"])

# Payme Error Codes
ERROR_INTERNAL_SYSTEM = -32400
ERROR_INSUFFICIENT_PRIVILEGE = -32504
ERROR_INVALID_JSON_RPC_OBJECT = -32600
ERROR_METHOD_NOT_FOUND = -32601
ERROR_INVALID_AMOUNT = -31001
ERROR_TRANSACTION_NOT_FOUND = -31003
ERROR_ORDER_NOT_FOUND = -31050
ERROR_ORDER_ALREADY_PAID = -31051
ERROR_COULD_NOT_CANCEL = -31007

@router.post("")
@router.post("/")
async def payme_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Rasmiy Payme JSON-RPC 2.0 Webhook Handler
    """
    try:
        data = await request.json()
    except Exception:
        return {"error": {"code": ERROR_INVALID_JSON_RPC_OBJECT, "message": "Invalid JSON"}, "id": None}

    req_id = data.get("id")
    method = data.get("method")
    params = data.get("params", {})

    if method == "CheckPerformTransaction":
        order_id = params.get("account", {}).get("order_id")
        amount = params.get("amount") # tiyinda

        if not order_id:
            return {"error": {"code": ERROR_ORDER_NOT_FOUND, "message": "Order not found"}, "id": req_id}

        res = await db.execute(select(Order).where(Order.id == int(order_id)))
        order = res.scalar_one_or_none()

        if not order:
            return {"error": {"code": ERROR_ORDER_NOT_FOUND, "message": "Order not found"}, "id": req_id}

        expected_amount_tiyin = int(order.total_amount * 100)
        if amount != expected_amount_tiyin:
            return {"error": {"code": ERROR_INVALID_AMOUNT, "message": "Invalid amount"}, "id": req_id}

        return {"result": {"allow": True}, "id": req_id}

    elif method == "CreateTransaction":
        order_id = params.get("account", {}).get("order_id")
        payme_trans_id = params.get("id")
        payme_time = params.get("time")
        amount = params.get("amount")

        res = await db.execute(select(Order).where(Order.id == int(order_id)))
        order = res.scalar_one_or_none()
        if not order:
            return {"error": {"code": ERROR_ORDER_NOT_FOUND, "message": "Order not found"}, "id": req_id}

        # Tranzaksiyani tekshirish
        tx_res = await db.execute(select(PaymentTransaction).where(PaymentTransaction.payme_transaction_id == payme_trans_id))
        tx = tx_res.scalar_one_or_none()

        if not tx:
            tx = PaymentTransaction(
                order_id=order.id,
                provider="payme",
                amount=int(amount / 100),
                payme_transaction_id=payme_trans_id,
                payme_time=payme_time,
                state=1,
                status="kutilmoqda"
            )
            db.add(tx)
            await db.commit()
            await db.refresh(tx)

        return {
            "result": {
                "create_time": tx.payme_time or int(time.time() * 1000),
                "transaction": str(tx.id),
                "state": tx.state
            },
            "id": req_id
        }

    elif method == "PerformTransaction":
        payme_trans_id = params.get("id")
        tx_res = await db.execute(select(PaymentTransaction).where(PaymentTransaction.payme_transaction_id == payme_trans_id))
        tx = tx_res.scalar_one_or_none()

        if not tx:
            return {"error": {"code": ERROR_TRANSACTION_NOT_FOUND, "message": "Transaction not found"}, "id": req_id}

        if tx.state == 1:
            perform_time = int(time.time() * 1000)
            tx.state = 2
            tx.payme_perform_time = perform_time
            tx.status = "muvaffaqiyatli"
            await db.commit()

            # Buyurtmani to'langan deb belgilash
            await mark_order_paid(db, tx.order_id, "payme", payme_trans_id, tx.amount)

        return {
            "result": {
                "transaction": str(tx.id),
                "perform_time": tx.payme_perform_time or int(time.time() * 1000),
                "state": tx.state
            },
            "id": req_id
        }

    elif method == "CheckTransaction":
        payme_trans_id = params.get("id")
        tx_res = await db.execute(select(PaymentTransaction).where(PaymentTransaction.payme_transaction_id == payme_trans_id))
        tx = tx_res.scalar_one_or_none()

        if not tx:
            return {"error": {"code": ERROR_TRANSACTION_NOT_FOUND, "message": "Transaction not found"}, "id": req_id}

        return {
            "result": {
                "create_time": tx.payme_time or 0,
                "perform_time": tx.payme_perform_time or 0,
                "cancel_time": tx.payme_cancel_time or 0,
                "transaction": str(tx.id),
                "state": tx.state,
                "reason": tx.payme_reason
            },
            "id": req_id
        }

    elif method == "CancelTransaction":
        payme_trans_id = params.get("id")
        reason = params.get("reason")
        tx_res = await db.execute(select(PaymentTransaction).where(PaymentTransaction.payme_transaction_id == payme_trans_id))
        tx = tx_res.scalar_one_or_none()

        if not tx:
            return {"error": {"code": ERROR_TRANSACTION_NOT_FOUND, "message": "Transaction not found"}, "id": req_id}

        cancel_time = int(time.time() * 1000)
        if tx.state == 1:
            tx.state = -1
        elif tx.state == 2:
            tx.state = -2
        tx.payme_cancel_time = cancel_time
        tx.payme_reason = reason
        tx.status = "bekor_qilindi"
        await db.commit()

        return {
            "result": {
                "transaction": str(tx.id),
                "cancel_time": cancel_time,
                "state": tx.state
            },
            "id": req_id
        }

    return {"error": {"code": ERROR_METHOD_NOT_FOUND, "message": "Method not found"}, "id": req_id}
