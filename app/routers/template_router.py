from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.template import BatteryTemplate
from pydantic import BaseModel

router = APIRouter(prefix="/templates", tags=["Phase 2: Template Management"])

# THIS is the Pydantic Schema for the JSON input
class TemplateCreate(BaseModel):
    model_name: str
    target_capacity_ah: float
    tolerance_ah: float = 0.05
    cell_count_required: int
    series_count: int = 0
    parallel_count: int = 0

@router.post("/")
def create_template(template: TemplateCreate, db: Session = Depends(get_db)):
    # Check if exists
    existing = db.query(BatteryTemplate).filter_by(model_name=template.model_name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Model already exists")
    
    # Convert Pydantic model to SQLAlchemy model
    new_template = BatteryTemplate(**template.model_dump())
    db.add(new_template)
    db.commit()
    db.refresh(new_template)
    return new_template

@router.get("/")
def list_templates(db: Session = Depends(get_db)):
    templates = db.query(BatteryTemplate).all()
    return templates