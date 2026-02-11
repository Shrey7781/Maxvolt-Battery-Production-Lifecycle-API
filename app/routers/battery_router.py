from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.battery import BatteryPack
from app.models.cell import Cell
from app.models.template import BatteryTemplate
from datetime import datetime
router = APIRouter(prefix="/battery-packs", tags=["Phase 2: Assembly"])

@router.post("/{battery_id}/link-cell/{cell_id}")
def link_cell_to_pack(battery_id: str, cell_id: str, db: Session = Depends(get_db)):
    # 1. Fetch the Pack and its linked Model Template
    pack = db.query(BatteryPack).filter_by(battery_id=battery_id).first()
    if not pack:
        raise HTTPException(status_code=404, detail="Battery Pack not found")
    
    # Pack is linked to template via model_name
    template = pack.template 

    # 2. Fetch the Cell and check availability
    cell = db.query(Cell).filter_by(cell_id=cell_id).first()
    if not cell:
        raise HTTPException(status_code=404, detail="Cell not found in inventory")
    
    if cell.is_used:
        raise HTTPException(status_code=400, detail="This cell is already part of another pack!")

    # 3. ABSOLUTE TARGET TOLERANCE CHECK
    # We compare against the Template's Target Capacity, NOT the first cell
    target = float(template.target_capacity_ah)
    tolerance = float(template.tolerance_ah)
    actual = float(cell.actual_cap_ah)

    lower_limit = target - tolerance
    upper_limit = target + tolerance

    if not (lower_limit <= actual <= upper_limit):
        raise HTTPException(
            status_code=400, 
            detail=(f"Tolerance Breach! Cell capacity {actual}Ah is outside the "
                    f"required range for {pack.model_name} ({lower_limit} - {upper_limit} Ah)")
        )

    # 4. CAPACITY COUNT CHECK
    if len(pack.cells) >= template.cell_count_required:
        raise HTTPException(status_code=400, detail="Pack assembly is already complete!")

    # 5. LINK AND LOCK
    pack.cells.append(cell)
    cell.is_used = True
    
    db.commit()

    return {
        "status": "Success",
        "cell_added": cell_id,
        "pack_fill": f"{len(pack.cells)}/{template.cell_count_required}",
        "target_range": f"{lower_limit} - {upper_limit} Ah"
    }




@router.post("/start-assembly")
def start_assembly(battery_id: str, model_name: str, db: Session = Depends(get_db)):
    # 1. Look up the rules for this model
    template = db.query(BatteryTemplate).filter_by(model_name=model_name).first()
    if not template:
        raise HTTPException(status_code=404, detail="Model template not found")

    # 2. Prevent duplicate battery serial numbers
    existing = db.query(BatteryPack).filter_by(battery_id=battery_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Battery ID already exists")

    # 3. Create the record
    new_pack = BatteryPack(
        battery_id=battery_id,
        model_name=model_name,
        assembly_date=datetime.now()
    )
    db.add(new_pack)
    db.commit()
    return {"status": "Success", "message": f"Pack {battery_id} is ready for assembly"}

from app.models.battery import PackTestResult

@router.post("/{battery_id}/submit-test")
def submit_pack_test(
    battery_id: str, 
    cap_ah: float, 
    working_mode: str, 
    db: Session = Depends(get_db)
):
    # 1. Verify pack exists
    pack = db.query(BatteryPack).filter_by(battery_id=battery_id).first()
    if not pack:
        raise HTTPException(status_code=404, detail="Battery Pack not found")

    # 2. Logic: Compare Pack Capacity to Template Target
    template = pack.template
    status = "PASS" if cap_ah >= float(template.target_capacity_ah) else "FAIL"

    # 3. Save the result
    test_result = PackTestResult(
        battery_id=battery_id,
        cap_ah=cap_ah,
        working_mode=working_mode,
        status=status
    )
    
    db.add(test_result)
    
    # Update the pack's final status based on the test
    pack.final_status = "TESTED_" + status
    
    db.commit()

    return {
        "battery_id": battery_id,
        "test_status": status,
        "measured_capacity": cap_ah,
        "target_required": template.target_capacity_ah
    }