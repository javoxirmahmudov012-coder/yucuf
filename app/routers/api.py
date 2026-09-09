from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.schemas import OrderCreateSchema, PromoCheckRequest, ReviewCreateSchema
from app.models.promo import PromoCode
from app.models.review import ProductReview
from app.services.order_service import create_order_from_cart
from app.services.payment_service import generate_payme_link, generate_click_link
from sqlalchemy import select

router = APIRouter(prefix="/api", tags=["API"])


@router.post("/create-order")
async def api_create_order(order_data: OrderCreateSchema, db: AsyncSession = Depends(get_db)):
    try:
        order = await create_order_from_cart(db, order_data)

        payment_redirect_url = None
        if order.payment_method == "payme":
            payment_redirect_url = generate_payme_link(order)
        elif order.payment_method == "click":
            payment_redirect_url = generate_click_link(order)

        return {
            "success": True,
            "order_id": order.id,
            "order_number": order.order_number,
            "total_amount": order.total_amount,
            "payment_method": order.payment_method,
            "payment_redirect_url": payment_redirect_url
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Buyurtma yaratishda xatolik: {str(e)}")


@router.post("/check-promo")
async def api_check_promo(req: PromoCheckRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(PromoCode).where(
        PromoCode.code == req.code.strip().upper(),
        PromoCode.is_active == True
    )
    res = await db.execute(stmt)
    promo = res.scalar_one_or_none()

    if not promo:
        return {"valid": False, "message": "Bunday promokod mavjud emas yoki muddati o'tgan."}

    discount = promo.calculate_discount(req.cart_total)
    if discount == 0:
        if req.cart_total < promo.min_order_amount:
            return {
                "valid": False,
                "message": f"Ushbu promokod minimal {promo.min_order_amount:,} so'mlik xarid uchun amal qiladi."
            }
        return {"valid": False, "message": "Promokod limiti tugagan."}

    return {
        "valid": True,
        "code": promo.code,
        "discount_amount": discount,
        "message": f"Chegirma: {discount:,} so'm"
    }


@router.post("/add-review")
async def api_add_review(rev_data: ReviewCreateSchema, db: AsyncSession = Depends(get_db)):
    review = ProductReview(
        product_id=rev_data.product_id,
        author_name=rev_data.author_name,
        author_city=rev_data.author_city or "Toshkent",
        rating=rev_data.rating,
        comment=rev_data.comment,
        is_verified_buyer=True,
        is_approved=True
    )
    db.add(review)
    await db.commit()
    return {"success": True, "message": "Sharh qabul qilindi"}
