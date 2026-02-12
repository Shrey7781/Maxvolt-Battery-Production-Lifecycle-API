from sqlalchemy import Column, String, Numeric, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.database import Base # Ensure this import is present!
from datetime import datetime

class Cell(Base):
    __tablename__ = "cells"

    cell_id = Column(String(100), primary_key=True, index=True)
    grading_date = Column(DateTime, default=datetime.now)
    
    # Use (10, 3) for high precision (e.g., 102.328 Ah)
    actual_cap_ah = Column(Numeric(10, 3))     
    ocv_volts = Column(Numeric(10, 3))         
    cut_off_voltage = Column(Numeric(10, 3))   
                  
    capacity_group = Column(String(50))       
    is_used = Column(Boolean, default=False)

    
    battery_packs = relationship("BatteryPack", secondary="pack_cell_mapping", back_populates="cells")
    grading_results = relationship("GradingStepResult", back_populates="cell", cascade="all, delete-orphan")
    def __repr__(self):
        return f"<Cell(id={self.cell_id}, capacity={self.actual_cap_ah})>"