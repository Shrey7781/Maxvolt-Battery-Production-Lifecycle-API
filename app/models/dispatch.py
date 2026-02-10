from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from app.database import Base
from datetime import datetime


class BatteryDispatch(Base):
    __tablename__ = "battery_dispatch"

    sale_id = Column(Integer, primary_key=True, index=True)
    battery_id = Column(Integer, ForeignKey("battery_packs.battery_id"), unique=True)
    customer_name = Column(String(255), nullable=False)
    invoice_number = Column(String(100))
    sale_date = Column(DateTime, default=datetime.utcnow)
    sales_executive_signature = Column(String(100))
