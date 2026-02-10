from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class BatteryTemplate(Base):
    __tablename__ = "battery_templates"

    template_id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), nullable=False)
    req_grading_cycle = Column(Integer, nullable=False)
    target_cap_ah = Column(Numeric(6, 2), nullable=False)
    tolerance_pct = Column(Numeric(5, 2), nullable=False)
    cell_count_req = Column(Integer, nullable=False)

    batteries = relationship("BatteryPack", back_populates="template")


class BatteryPack(Base):
    __tablename__ = "battery_packs"

    battery_id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("battery_templates.template_id"))
    bms_serial_no = Column(String(100), unique=True, nullable=False)
    assembly_date = Column(Date, nullable=False)
    final_status = Column(String(50), default="ASSEMBLED")

    template = relationship("BatteryTemplate", back_populates="batteries")


pack_cell_mapping = Table(
    "pack_cell_mapping",
    Base.metadata,
    Column("battery_id", Integer, ForeignKey("battery_packs.battery_id"), primary_key=True),
    Column("cell_id", String(100), ForeignKey("cells.cell_id"), primary_key=True),
)

