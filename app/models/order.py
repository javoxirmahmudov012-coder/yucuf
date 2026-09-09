from sqlalchemy import Column, Integer, String, Text, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
import random
import string
from app.database import Base

def generate_order_number():
    digits = ''.join(random.choices(string.digits, k=6))
    return f"KS-{digits}"

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(20), unique=True, default=generate_order_number, index=True)
    
    # Mijoz ma'lumotlari
    customer_name = Column(String(150), nullable=False)
    customer_phone = Column(String(30), nullable=False, index=True)
    customer_email = Column(String(150), nullable=True)
    
    # Manzil va yetkazib berish
    region = Column(String(100), default="Toshkent shahri")     # Toshkent shahri / Samarqand / Farg'ona ...
    district = Column(String(100), nullable=True)
    address = Column(String(300), nullable=False)
    landmark = Column(String(200), nullable=True)               # Mo'ljal
    delivery_notes = Column(Text, nullable=True)                # Kuryer uchun eslatma
    delivery_method = Column(String(50), default="standard")    # "standard", "express", "pickup"
    delivery_fee = Column(Integer, default=25000)
    
    # Hisob-kitob
    items_total = Column(Integer, default=0)
    discount_amount = Column(Integer, default=0)
    promo_code = Column(String(50), nullable=True)
    total_amount = Column(Integer, nullable=False)
    
    # To'lov ma'lumotlari
    payment_method = Column(String(50), default="payme")        # "payme", "click", "cash"
    payment_status = Column(String(50), default="kutilmoqda")   # "kutilmoqda", "tolandi", "qaytarildi", "xato"
    paid_at = Column(DateTime, nullable=True)
    
    # Buyurtma holati
    # "yangi" -> "qabul_qilindi" -> "tayyorlanmoqda" -> "yolda" -> "yetkazildi" -> "bekor_qilindi"
    status = Column(String(50), default="yangi", index=True)
    courier_name = Column(String(100), nullable=True)
    courier_phone = Column(String(30), nullable=True)
    tracking_code = Column(String(100), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payments = relationship("PaymentTransaction", back_populates="order", cascade="all, delete-orphan")

    @property
    def status_label(self) -> str:
        labels = {
            "yangi": "Yangi buyurtma",
            "qabul_qilindi": "Qabul qilindi",
            "tayyorlanmoqda": "Sklad tayyorlamoqda",
            "yolda": "Kuryer yetkazmoqda",
            "yetkazildi": "Yetkazildi",
            "bekor_qilindi": "Bekor qilindi"
        }
        return labels.get(self.status, self.status)

    @property
    def status_badge_class(self) -> str:
        classes = {
            "yangi": "bg-blue-100 text-blue-800 border-blue-200",
            "qabul_qilindi": "bg-purple-100 text-purple-800 border-purple-200",
            "tayyorlanmoqda": "bg-amber-100 text-amber-800 border-amber-200",
            "yolda": "bg-indigo-100 text-indigo-800 border-indigo-200",
            "yetkazildi": "bg-emerald-100 text-emerald-800 border-emerald-200",
            "bekor_qilindi": "bg-rose-100 text-rose-800 border-rose-200"
        }
        return classes.get(self.status, "bg-gray-100 text-gray-800")

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    
    product_title = Column(String(200), nullable=False)
    product_artist = Column(String(200), nullable=False)
    product_image = Column(String(500), nullable=True)
    price = Column(Integer, nullable=False)
    quantity = Column(Integer, default=1)
    subtotal = Column(Integer, nullable=False)
    
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
