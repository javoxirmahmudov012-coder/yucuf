from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class CartItemSchema(BaseModel):
    product_id: int
    quantity: int = Field(default=1, ge=1)

class OrderCreateSchema(BaseModel):
    customer_name: str = Field(..., min_length=2, max_length=100)
    customer_phone: str = Field(..., min_length=9, max_length=25)
    customer_email: Optional[str] = None
    region: str = "Toshkent shahri"
    district: Optional[str] = None
    address: str = Field(..., min_length=5)
    landmark: Optional[str] = None
    delivery_notes: Optional[str] = None
    delivery_method: str = "standard" # standard / express
    payment_method: str = "payme"     # payme / click / cash
    promo_code: Optional[str] = None
    items: List[CartItemSchema]

class PromoCheckRequest(BaseModel):
    code: str
    cart_total: int

class ReviewCreateSchema(BaseModel):
    product_id: int
    author_name: str
    author_city: Optional[str] = "Toshkent"
    rating: int = Field(default=5, ge=1, le=5)
    comment: str = Field(..., min_length=3)

class ProductFormSchema(BaseModel):
    title: str
    artist: str
    genre: str
    release_year: Optional[int] = 1995
    condition: str = "Original Vintage"
    tape_type: str = "Type I (Normal)"
    duration_minutes: int = 60
    country: str = "O'zbekiston"
    label: str = "Tarona Records"
    price: int
    old_price: Optional[int] = None
    stock: int = 5
    is_featured: bool = False
    is_new: bool = True
    image_url: Optional[str] = None
    audio_sample_url: Optional[str] = None
    audio_sample_title: Optional[str] = None
    description: Optional[str] = None
    tracklist_a: Optional[str] = None
    tracklist_b: Optional[str] = None

class OrderStatusUpdateSchema(BaseModel):
    status: str
    courier_name: Optional[str] = None
    courier_phone: Optional[str] = None
    tracking_code: Optional[str] = None
