from sqlalchemy import Column, Integer, String, Numeric
from sqlalchemy.orm import relationship
from app.database import Base

class BatteryTemplate(Base):
    __tablename__ = "battery_templates"

    template_id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), unique=True, nullable=False) # e.g., "12V100Ah-NPD"
    target_capacity_ah = Column(Numeric(6, 2))                    # e.g., 100.00
    tolerance_ah = Column(Numeric(4, 2), default=0.05)            # Your 0.05Ah rule
    cell_count_required = Column(Integer)                         # e.g., 16

    # Relationship back to packs
    packs = relationship("BatteryPack", back_populates="template")