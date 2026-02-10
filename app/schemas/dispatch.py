# app/schemas/dispatch.py
from pydantic import BaseModel
from datetime import datetime

class BatteryDispatchCreate(BaseModel):
    battery_id: int
    customer_name: str
    invoice_number: str
    sales_executive_signature: str

class BatteryDispatchResponse(BatteryDispatchCreate):
    sale_id: int
    sale_date: datetime

    class Config:
        from_attributes = True