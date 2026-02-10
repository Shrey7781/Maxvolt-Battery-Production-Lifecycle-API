# app/schemas/pdi.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class PDIResultCreate(BaseModel):
    checkpoint_id: int
    status: bool

class PDISessionCreate(BaseModel):
    battery_id: int
    qc_signature: str
    remark: Optional[str] = None
    results: List[PDIResultCreate]  # This allows sending all 20+ checks in one go

class PDISessionResponse(BaseModel):
    pdi_id: int
    battery_id: int
    inspection_date: date
    
    class Config:
        from_attributes = True