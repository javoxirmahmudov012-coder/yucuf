from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime
from datetime import datetime
from app.database import Base

class PromoCode(Base):
    __tablename__ = "promo_codes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(200), nullable=True)
    
    discount_type = Column(String(20), default="percent") # "percent" or "fixed"
    discount_value = Column(Integer, nullable=False)      # masalan: 10 (%) yoki 25000 (so'm)
    min_order_amount = Column(Integer, default=0)         # Minimal buyurtma summasi
    
    max_uses = Column(Integer, default=100)
    used_count = Column(Integer, default=0)
    
    is_active = Column(Boolean, default=True)
    valid_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def calculate_discount(self, total_items_amount: int) -> int:
        if not self.is_active:
            return 0
        if self.valid_until and datetime.utcnow() > self.valid_until:
            return 0
        if total_items_amount < self.min_order_amount:
            return 0
        if self.used_count >= self.max_uses:
            return 0
            
        if self.discount_type == "percent":
            return int((total_items_amount * self.discount_value) / 100)
        elif self.discount_type == "fixed":
            return min(self.discount_value, total_items_amount)
        return 0
