from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class ProductReview(Base):
    __tablename__ = "product_reviews"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    author_name = Column(String(100), nullable=False)
    author_city = Column(String(100), default="Toshkent")
    rating = Column(Integer, default=5) # 1 to 5
    comment = Column(Text, nullable=False)
    is_verified_buyer = Column(Boolean, default=True)
    is_approved = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    product = relationship("Product", back_populates="reviews")
