from sqlalchemy import Column, Integer, String, Text, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    slug = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    icon = Column(String(50), default="disc")
    
    products = relationship("Product", back_populates="category")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    artist = Column(String(200), nullable=False, index=True)
    slug = Column(String(220), nullable=False, unique=True, index=True)
    
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    genre = Column(String(100), nullable=False, index=True) # Pop, Rock, Retro O'zbek, Synthwave, Hip-Hop, Jazz, Blank
    
    release_year = Column(Integer, nullable=True)
    condition = Column(String(50), default="Original Vintage") # "Yangi muhrlangan", "Original Vintage", "Kolleksion"
    tape_type = Column(String(50), default="Type I (Normal)")  # "Type I (Normal)", "Type II (High/CrO2)", "Type IV (Metal)"
    duration_minutes = Column(Integer, default=60)              # 60 min, 90 min
    country = Column(String(100), default="O'zbekiston / SSSR")
    label = Column(String(100), default="Melodiya / Tarona Records")
    
    price = Column(Integer, nullable=False)                     # UZS
    old_price = Column(Integer, nullable=True)                 # Chegirma uchun
    stock = Column(Integer, default=5)
    is_featured = Column(Boolean, default=False)
    is_new = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    
    image_url = Column(String(500), default="/static/images/cassette_default.jpg")
    audio_sample_url = Column(String(500), nullable=True)      # MP3 sample preview for audio player
    audio_sample_title = Column(String(200), nullable=True)    # Nomlanishi (masalan: Yalla - Majnuntol)
    
    description = Column(Text, nullable=True)
    tracklist_a = Column(Text, nullable=True)                  # A-tomoni treklari (JSON yoki qatorma-qator)
    tracklist_b = Column(Text, nullable=True)                  # B-tomoni treklari
    
    views_count = Column(Integer, default=0)
    sales_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    category = relationship("Category", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")
    reviews = relationship("ProductReview", back_populates="product", cascade="all, delete-orphan")

    @property
    def discount_percent(self) -> int:
        if self.old_price and self.old_price > self.price:
            return int(((self.old_price - self.price) / self.old_price) * 100)
        return 0

    @property
    def average_rating(self) -> float:
        if not self.reviews:
            return 5.0
        ratings = [r.rating for r in self.reviews if r.is_approved]
        return round(sum(ratings) / len(ratings), 1) if ratings else 5.0
