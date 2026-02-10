from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.database import Base

# Bridge table for Battery-Cell Mapping
pack_cell_mapping = Table(
    "pack_cell_mapping",
    Base.metadata,
    Column("battery_id", Integer, ForeignKey("battery_packs.battery_id", ondelete="CASCADE"), primary_key=True),
    Column("cell_id", String(100), ForeignKey("cells.cell_id", ondelete="RESTRICT"), primary_key=True),
)

class BatteryPack(Base):
    __tablename__ = "battery_packs"
    battery_id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("battery_templates.template_id"))
    bms_serial_no = Column(String(100), unique=True, nullable=True)
    assembly_date = Column(Date, nullable=False)
    final_status = Column(String(50), default="ASSEMBLED")

    template = relationship("BatteryTemplate")
    cells = relationship("Cell", secondary=pack_cell_mapping, back_populates="battery_packs")
    
    # Add this relationship so you can access test results from the pack
    test_results = relationship("PackTestResult", back_populates="battery")

# --- THIS IS THE MISSING CLASS ---
class PackTestResult(Base):
    __tablename__ = "pack_test_results"
    
    test_id = Column(Integer, primary_key=True, index=True)
    battery_id = Column(Integer, ForeignKey("battery_packs.battery_id", ondelete="CASCADE"))
    working_mode = Column(String(100)) # e.g., 'CD' for Discharge
    end_v = Column(Numeric(6, 2))
    end_a = Column(Numeric(6, 2))
    cap_ah = Column(Numeric(6, 2))
    status = Column(String(50)) # 'Pass' or 'Fail'

    battery = relationship("BatteryPack", back_populates="test_results")