from sqlalchemy import Column, String, Integer, Numeric, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.database import Base

class Cell(Base):
    __tablename__ = "cells"

    # Primary Identifier (Barcode Scan)
    cell_id = Column(String(100), primary_key=True, index=True)
    
    # Grading Results (Extracted from CSV)
    grading_cycle = Column(Numeric(3, 1)) # Stores 0.3, 0.5, etc.
    grading_date = Column(DateTime)
    actual_cap_ah = Column(Numeric(6, 2))     # The capacity from CC-D step
    ocv_volts = Column(Numeric(5, 3))         # Open Circuit Voltage
    acir_mohm = Column(Numeric(6, 2))         # Internal Resistance
                  # Date from machine file
    
    # Sorting & Inventory Status
    capacity_group = Column(String(50))       # e.g., "Group A", "Group B"
    is_used = Column(Boolean, default=False)  # TRUE once mapped to a pack

    # --- Relationships ---
    
    # Allows you to call cell.grading_results to see all steps for this cell
    grading_results = relationship("GradingStepResult", back_populates="cell", cascade="all, delete-orphan")
    
    # Links back to the pack cell mapping (via the bridge table in battery.py)
    # This allows you to see which pack a cell belongs to
    battery_packs = relationship("BatteryPack", secondary="pack_cell_mapping", back_populates="cells")

    def __repr__(self):
        return f"<Cell(id={self.cell_id}, capacity={self.actual_cap_ah}, is_used={self.is_used})>"