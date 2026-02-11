from sqlalchemy import Column, Integer, Boolean, String, Date, Numeric, ForeignKey, Table, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

# Bridge table for Battery-Cell Mapping
pack_cell_mapping = Table(
    "pack_cell_mapping",
    Base.metadata,
    Column("battery_id", String(100), ForeignKey("battery_packs.battery_id", ondelete="CASCADE"), primary_key=True),
    Column("cell_id", String(100), ForeignKey("cells.cell_id", ondelete="RESTRICT"), primary_key=True),
)

class BatteryPack(Base):
    __tablename__ = "battery_packs"
    
    battery_id = Column(String(100), primary_key=True, index=True)
    model_name = Column(String(100), ForeignKey("battery_templates.model_name"))
    
    # FIX: Change this to a Foreign Key to link to BMSInventory
    bms_id = Column(String(100), ForeignKey("bms_inventory.bms_id"), unique=True, nullable=True)
    
    assembly_date = Column(DateTime, nullable=False) # DateTime is better for precise tracking
    final_status = Column(String(50), default="ASSEMBLED")
    pdi_record = relationship("PDIChecklist", back_populates="battery", uselist=False)

    # Relationships
    template = relationship("BatteryTemplate", back_populates="packs")
    cells = relationship("Cell", secondary=pack_cell_mapping, back_populates="battery_packs")
    test_results = relationship("PackTestResult", back_populates="battery")
    
    # Link to the BMS unit
    bms_unit = relationship("BMSInventory", back_populates="mounted_pack")

class PackTestResult(Base):
    __tablename__ = "pack_test_results"
    
    test_id = Column(Integer, primary_key=True, index=True)
    battery_id = Column(String(100), ForeignKey("battery_packs.battery_id"))
    working_mode = Column(String(100)) 
    end_v = Column(Numeric(10, 3))
    end_a = Column(Numeric(10, 3))
    cap_ah = Column(Numeric(10, 3))
    
    energy_wh = Column(Numeric(10, 3))
    test_duration_min = Column(Numeric(10, 2))
    avg_voltage = Column(Numeric(10, 3))

    status = Column(String(50)) 
    battery = relationship("BatteryPack", back_populates="test_results")

class BMSInventory(Base):
    __tablename__ = "bms_inventory"
    
    bms_id = Column(String(100), primary_key=True)
    bms_model = Column(String(100))
    is_used = Column(Boolean, default=False)
    
    # Relationship back to the battery pack
    mounted_pack = relationship("BatteryPack", back_populates="bms_unit", uselist=False)

class PDIChecklist(Base):
    __tablename__ = "pdi_checklists"
    
    id = Column(Integer, primary_key=True, index=True)
    battery_id = Column(String(100), ForeignKey("battery_packs.battery_id"))
    
    # Visual & Mechanical Checkpoints
    visual_finish_ok = Column(Boolean, default=False)
    terminal_tightness_ok = Column(Boolean, default=False)
    internal_wiring_routing_ok = Column(Boolean, default=False)
    handle_secure_ok = Column(Boolean, default=False)
    sticker_labeling_ok = Column(Boolean, default=False)

    # Electrical & Safety Checkpoints
    bms_communication_ok = Column(Boolean, default=False)
    short_circuit_test_ok = Column(Boolean, default=False)
    final_ocv_v = Column(Numeric(10, 3))
    polarity_check_ok = Column(Boolean, default=False)

    # Documentation Checkpoints
    warranty_seal_applied = Column(Boolean, default=False)
    accessories_included = Column(Boolean, default=False)
    
    # Metadata
    inspector_name = Column(String(100))
    inspection_timestamp = Column(DateTime, default=datetime.now)
    final_result = Column(String(20)) # 'PASS' or 'FAIL'
    remarks = Column(String(255), nullable=True)

    # Relationship back to the battery pack
    battery = relationship("BatteryPack", back_populates="pdi_record")
    BatteryPack.pdi_record = relationship("PDIChecklist", back_populates="battery", uselist=False)