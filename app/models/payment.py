from sqlalchemy import Column, Integer, String, Text, Float, Boolean, ForeignKey, DateTime, BigInteger
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    
    provider = Column(String(50), nullable=False)               # "payme" or "click"
    amount = Column(Integer, nullable=False)                    # UZS
    state = Column(Integer, default=1)                          # Payme: 1 (created), 2 (completed), -1/-2 (cancelled)
    
    # Payme specific fields
    payme_transaction_id = Column(String(100), nullable=True, index=True)
    payme_time = Column(BigInteger, nullable=True)
    payme_perform_time = Column(BigInteger, nullable=True)
    payme_cancel_time = Column(BigInteger, nullable=True)
    payme_reason = Column(Integer, nullable=True)
    
    # Click specific fields
    click_trans_id = Column(String(100), nullable=True, index=True)
    click_paydoc_id = Column(String(100), nullable=True)
    merchant_trans_id = Column(String(100), nullable=True)
    
    status = Column(String(50), default="kutilmoqda")           # "kutilmoqda", "muvaffaqiyatli", "bekor_qilindi"
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    order = relationship("Order", back_populates="payments")
