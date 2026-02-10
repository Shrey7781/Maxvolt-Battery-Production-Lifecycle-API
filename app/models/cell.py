from sqlalchemy import Column, String, Integer, Numeric, Boolean, Date
from app.database import Base


class Cell(Base):
    __tablename__ = "cells"

    cell_id = Column(String(100), primary_key=True, index=True)
    grading_cycle = Column(Integer)
    actual_cap_ah = Column(Numeric(6, 2))
    ocv_volts = Column(Numeric(5, 3))
    acir_mohm = Column(Numeric(6, 2))
    grading_date = Column(Date)
    capacity_group = Column(String(10))
    is_used = Column(Boolean, default=False)
