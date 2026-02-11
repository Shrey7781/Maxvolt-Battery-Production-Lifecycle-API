from sqlalchemy import Column, String, Integer, Numeric
from sqlalchemy.orm import relationship
from app.database import Base

class BatteryTemplate(Base):
    __tablename__ = "battery_templates"

    model_name = Column(String(100), primary_key=True) 
    target_capacity_ah = Column(Numeric(6, 2), nullable=False)
    tolerance_ah = Column(Numeric(4, 2), default=0.05) 
    cell_count_required = Column(Integer, nullable=False)
    series_count = Column(Integer, default=0)
    parallel_count = Column(Integer, default=0)

    # Relationship back to packs
    packs = relationship("BatteryPack", back_populates="template")