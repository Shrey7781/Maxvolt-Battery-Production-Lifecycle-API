# app/schemas/battery.py
class PackCellMappingCreate(BaseModel):
    battery_id: int
    cell_id: str