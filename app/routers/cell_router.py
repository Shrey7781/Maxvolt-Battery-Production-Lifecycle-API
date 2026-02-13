from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.cell import Cell
from app.services.cell_service import CellService # Unified service import

router = APIRouter(prefix="/cells", tags=["Phase 1: Cell Management"])

# STEP 1: SCAN & REGISTER
@router.post("/register/{cell_id}")
def register_cell(cell_id: str, db: Session = Depends(get_db)):
    # Check if cell exists
    existing = db.query(Cell).filter(Cell.cell_id == cell_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Cell ID already exists")
    
    new_cell = Cell(cell_id=cell_id, is_used=False)
    db.add(new_cell)
    db.commit()
    db.refresh(new_cell) # Best practice to refresh after commit
    return {"message": "Cell registered successfully", "cell": new_cell}

# STEP 2: GET DETAILS
@router.get("/{cell_id}")
def get_cell_details(cell_id: str, db: Session = Depends(get_db)):
    cell = db.query(Cell).filter(Cell.cell_id == cell_id).first()
    if not cell:
        raise HTTPException(status_code=404, detail="Cell not found")
    return cell

# STEP 3: PROCESS GRADING
@router.post("/auto-link-grading")
async def auto_link_grading(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    # Ensure CellService.process_grading_excel is an 'async' function 
    # if you are 'awaiting' it here.
    return await CellService.process_grading_excel(db, content)