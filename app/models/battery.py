from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.database import Base

# Bridge table for Battery-Cell Mapping
pack_cell_mapping = Table(
    "pack_cell_mapping",
    Base.metadata,
    Column("battery_id", String(100), ForeignKey("battery_packs.battery_id", ondelete="CASCADE"), primary_key=True),
    Column("cell_id", String(100), ForeignKey("cells.cell_id", ondelete="RESTRICT"), primary_key=True),
)

class BatteryPack(Base):
    __tablename__ = "battery_packs"
    
    # Changed to String to accommodate physical barcodes/serial numbers
    battery_id = Column(String(100), primary_key=True, index=True)
    
    # KEY FIX: Link to model_name instead of template_id
    model_name = Column(String(100), ForeignKey("battery_templates.model_name"))
    
    bms_serial_no = Column(String(100), unique=True, nullable=True)
    assembly_date = Column(Date, nullable=False)
    final_status = Column(String(50), default="ASSEMBLED")

    # Relationships
    template = relationship("BatteryTemplate", back_populates="packs")
    cells = relationship("Cell", secondary=pack_cell_mapping, back_populates="battery_packs")
    test_results = relationship("PackTestResult", back_populates="battery")

class PackTestResult(Base):
    __tablename__ = "pack_test_results"
    
    test_id = Column(Integer, primary_key=True, index=True)
    battery_id = Column(String(100), ForeignKey("battery_packs.battery_id"))
    working_mode = Column(String(100)) 
    end_v = Column(Numeric(6, 2))
    end_a = Column(Numeric(6, 2))
    cap_ah = Column(Numeric(6, 2))
    status = Column(String(50)) 

    battery = relationship("BatteryPack", back_populates="test_results")