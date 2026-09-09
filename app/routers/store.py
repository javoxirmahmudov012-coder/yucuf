from fastapi import APIRouter, Depends, Request, Query, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from sqlalchemy.orm import selectinload
from pathlib import Path

from app.database import get_db
from app.models.product import Category, Product
from app.models.order import Order
from app.models.review import ProductReview

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def home_page(request: Request, db: AsyncSession = Depends(get_db)):
    # Kategoriyalar
    cat_res = await db.execute(select(Category))
    categories = cat_res.scalars().all()

    # Ommabop kassetalar (Featured)
    prod_stmt = select(Product).where(Product.is_active == True, Product.is_featured == True).limit(8)
    prod_res = await db.execute(prod_stmt)
    featured_products = prod_res.scalars().all()
    
    if len(featured_products) < 4:
        all_p = await db.execute(select(Product).where(Product.is_active == True).limit(8))
        featured_products = all_p.scalars().all()

    # So'nggi sharhlar
    rev_stmt = select(ProductReview).where(ProductReview.is_approved == True).order_by(ProductReview.created_at.desc()).limit(3)
    rev_res = await db.execute(rev_stmt)
    latest_reviews = rev_res.scalars().all()

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "categories": categories,
            "featured_products": featured_products,
            "latest_reviews": latest_reviews
        }
    )

@router.get("/catalog", response_class=HTMLResponse)
async def catalog_page(
    request: Request,
    genre: str = Query(None),
    condition: str = Query(None),
    tape_type: str = Query(None),
    q: str = Query(None),
    sort: str = Query(None),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Product).where(Product.is_active == True)

    if genre:
        stmt = stmt.where(Product.genre == genre)
    if condition:
        stmt = stmt.where(Product.condition == condition)
    if tape_type:
        stmt = stmt.where(Product.tape_type == tape_type)
    if q:
        search_query = f"%{q.strip()}%"
        stmt = stmt.where(
            or_(
                Product.title.ilike(search_query),
                Product.artist.ilike(search_query),
                Product.genre.ilike(search_query),
                Product.label.ilike(search_query)
            )
        )

    if sort == "price_asc":
        stmt = stmt.order_by(Product.price.asc())
    elif sort == "price_desc":
        stmt = stmt.order_by(Product.price.desc())
    elif sort == "oldest":
        stmt = stmt.order_by(Product.release_year.asc())
    else:
        stmt = stmt.order_by(Product.created_at.desc())

    res = await db.execute(stmt)
    products = res.scalars().all()

    # Barcha mavjud janrlar ro'yxati
    genres_res = await db.execute(select(Product.genre).distinct())
    genres = [g[0] for g in genres_res.all() if g[0]]

    return templates.TemplateResponse(
        request=request,
        name="catalog.html",
        context={
            "products": products,
            "genres": genres,
            "current_genre": genre,
            "current_condition": condition,
            "current_tape_type": tape_type,
            "current_q": q,
            "current_sort": sort
        }
    )

@router.get("/product/{slug}", response_class=HTMLResponse)
async def product_detail_page(slug: str, request: Request, db: AsyncSession = Depends(get_db)):
    stmt = select(Product).where(Product.slug == slug).options(selectinload(Product.reviews))
    res = await db.execute(stmt)
    product = res.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Kasseta topilmadi")

    # Ko'rishlar sonini oshirish
    product.views_count += 1
    await db.commit()

    # O'xshash kassetalar
    rel_stmt = select(Product).where(Product.genre == product.genre, Product.id != product.id).limit(4)
    rel_res = await db.execute(rel_stmt)
    related_products = rel_res.scalars().all()

    return templates.TemplateResponse(
        request=request,
        name="product.html",
        context={
            "product": product,
            "related_products": related_products
        }
    )

@router.get("/cart", response_class=HTMLResponse)
async def cart_page(request: Request):
    return templates.TemplateResponse(request=request, name="cart.html", context={})

@router.get("/checkout", response_class=HTMLResponse)
async def checkout_page(request: Request):
    return templates.TemplateResponse(request=request, name="checkout.html", context={})

@router.get("/payment/success/{order_id}", response_class=HTMLResponse)
async def payment_success_page(order_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    stmt = select(Order).where(Order.id == order_id).options(selectinload(Order.items))
    res = await db.execute(stmt)
    order = res.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="Buyurtma topilmadi")

    return templates.TemplateResponse(
        request=request,
        name="payment_success.html",
        context={
            "order": order
        }
    )

@router.get("/tracking", response_class=HTMLResponse)
async def tracking_page(request: Request, q: str = Query(None), order: str = Query(None), db: AsyncSession = Depends(get_db)):
    query = q or order
    found_order = None
    if query:
        search_val = query.strip()
        stmt = select(Order).where(
            or_(
                Order.order_number == search_val,
                Order.customer_phone == search_val,
                Order.customer_phone.ilike(f"%{search_val}%")
            )
        ).options(selectinload(Order.items)).order_by(Order.created_at.desc())
        res = await db.execute(stmt)
        found_order = res.scalars().first()

    return templates.TemplateResponse(
        request=request,
        name="tracking.html",
        context={
            "order": found_order,
            "query": query
        }
    )

@router.get("/about", response_class=HTMLResponse)
async def about_page(request: Request):
    return templates.TemplateResponse(request=request, name="about.html", context={})

@router.get("/contact", response_class=HTMLResponse)
async def contact_page(request: Request):
    return templates.TemplateResponse(request=request, name="contact.html", context={})

@router.get("/faq", response_class=HTMLResponse)
async def faq_page(request: Request):
    return templates.TemplateResponse(request=request, name="faq.html", context={})
