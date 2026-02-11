from sqlalchemy import Column, Integer, String, Date, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class PDICheckpoint(Base):
    """Master list of all checkpoints (e.g., 'Visual Finish', 'Terminal Tightness')"""
    __tablename__ = "pdi_checkpoints"
    
    checkpoint_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False) # e.g. "Visual Case Inspection"
    category = Column(String(50))              # e.g. "Mechanical"
    description = Column(Text)

class PDISession(Base):
    """One session per battery pack inspection"""
    __tablename__ = "pdi_sessions"
    
    pdi_id = Column(Integer, primary_key=True, index=True)
    
    # FIX: Must be String(100) to match BatteryPack.battery_id
    battery_id = Column(String(100), ForeignKey("battery_packs.battery_id"), unique=True)
    
    inspection_date = Column(Date)
    qc_signature = Column(String(150))
    remark = Column(Text)
    
    # Relationships
    results = relationship("PDIResult", back_populates="session")
    battery = relationship("BatteryPack") # Optional: to access battery details

class PDIResult(Base):
    """The pass/fail result for each individual checkpoint in a session"""
    __tablename__ = "pdi_results"
    
    result_id = Column(Integer, primary_key=True, index=True)
    pdi_id = Column(Integer, ForeignKey("pdi_sessions.pdi_id"))
    checkpoint_id = Column(Integer, ForeignKey("pdi_checkpoints.checkpoint_id"))
    status = Column(Boolean) # TRUE for Pass, FALSE for Fail

    session = relationship("PDISession", back_populates="results")
    checkpoint = relationship("PDICheckpoint")