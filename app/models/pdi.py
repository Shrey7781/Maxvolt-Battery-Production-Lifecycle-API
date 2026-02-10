from sqlalchemy import Column, Integer, String, Date, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class PDISession(Base):
    __tablename__ = "pdi_sessions"

    pdi_id = Column(Integer, primary_key=True, index=True)
    battery_id = Column(Integer, ForeignKey("battery_packs.battery_id"), unique=True)
    inspection_date = Column(Date)
    qc_signature = Column(String(150))
    remark = Column(Text)


class PDICheckpoint(Base):
    __tablename__ = "pdi_checkpoints"

    checkpoint_id = Column(Integer, primary_key=True, index=True)
    parameter_group = Column(String(100))
    description = Column(String)
    inspection_method = Column(String(100))
    category = Column(String(1))


class PDIResult(Base):
    __tablename__ = "pdi_results"

    result_id = Column(Integer, primary_key=True, index=True)
    pdi_id = Column(Integer, ForeignKey("pdi_sessions.pdi_id"))
    checkpoint_id = Column(Integer, ForeignKey("pdi_checkpoints.checkpoint_id"))
    status = Column(Boolean)
