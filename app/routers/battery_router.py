import io
import pandas as pd
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.battery import BatteryPack, PackTestResult
from app.models.cell import Cell
from app.models.template import BatteryTemplate
from app.models.battery import BatteryPack, PackTestResult, BMSInventory

router = APIRouter(prefix="/battery-packs", tags=["Phase 2 & 3: Assembly & Testing"])

# --- PHASE 2: ASSEMBLY ENDPOINTS ---

@router.post("/start-assembly")
def start_assembly(battery_id: str, model_name: str, db: Session = Depends(get_db)):
    template = db.query(BatteryTemplate).filter_by(model_name=model_name).first()
    if not template:
        raise HTTPException(status_code=404, detail="Model template not found")

    existing = db.query(BatteryPack).filter_by(battery_id=battery_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Battery ID already exists")

    new_pack = BatteryPack(
        battery_id=battery_id,
        model_name=model_name,
        assembly_date=datetime.now(),
        final_status="IN_PROGRESS"
    )
    db.add(new_pack)
    db.commit()
    return {"status": "Success", "message": f"Pack {battery_id} initialized"}

@router.post("/{battery_id}/link-cell/{cell_id}")
def link_cell_to_pack(battery_id: str, cell_id: str, db: Session = Depends(get_db)):
    pack = db.query(BatteryPack).filter_by(battery_id=battery_id).first()
    if not pack:
        raise HTTPException(status_code=404, detail="Battery Pack not found")
    
    template = pack.template 
    cell = db.query(Cell).filter_by(cell_id=cell_id).first()
    
    if not cell:
        raise HTTPException(status_code=404, detail="Cell not found")
    if cell.is_used:
        raise HTTPException(status_code=400, detail="Cell already in use")

    # Tolerance check
    target = float(template.target_capacity_ah)
    tolerance = float(template.tolerance_ah)
    actual = float(cell.actual_cap_ah)

    if not (target - tolerance <= actual <= target + tolerance):
        raise HTTPException(status_code=400, detail="Capacity Tolerance Breach")

    if len(pack.cells) >= template.cell_count_required:
        raise HTTPException(status_code=400, detail="Pack is full")

    pack.cells.append(cell)
    cell.is_used = True
    db.commit()
    return {"status": "Linked", "current_count": len(pack.cells)}

# --- PHASE 3: PACK GRADING (EXCEL PARSING) ---



@router.post("/upload-pack-test")
async def upload_pack_test(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # 1. Load Excel with multiple sheets
    content = await file.read()
    try:
        excel_data = pd.ExcelFile(io.BytesIO(content))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid Excel file")

    # 2. Extract Battery ID from 'Template Info' sheet (Header)
    # The snippet shows Barcode is in the first row/cell
    info_df = excel_data.parse("Template Info", header=None)
    raw_barcode = str(info_df.iloc[0, 0]) 
    battery_id = raw_barcode.replace("Barcode:", "").strip()

    # 3. Extract Metrics from 'Step Layer' sheet
    step_df = excel_data.parse("Step Layer")
    
    # We look for the 'Discharge' process as found in your Step Layer snippet
    discharge_data = step_df[step_df['Process'] == 'Discharge']
    if discharge_data.empty:
        raise HTTPException(status_code=400, detail="No 'Discharge' step found in file")
    
    stats = discharge_data.iloc[0]
    measured_cap = float(stats['Discharge Capacity(Ah)'])

    # 4. Validation against DB
    pack = db.query(BatteryPack).filter_by(battery_id=battery_id).first()
    if not pack:
        raise HTTPException(status_code=404, detail=f"Pack {battery_id} not registered in assembly")

    template = pack.template
    status = "PASS" if measured_cap >= float(template.target_capacity_ah) else "FAIL"

    # 5. Create Test Result with enhanced attributes from Step Layer
    test_result = PackTestResult(
    battery_id=battery_id,
    working_mode="Discharge",
    cap_ah=float(measured_cap),  # <--- Convert here
    end_v=float(stats['End Volt(V)']), # <--- Convert here
    end_a=float(stats['Set Current(A)']), # <--- Convert here
    energy_wh=float(stats.get('Discharge Energy(Wh)', 0)), # <--- Convert here
    test_duration_min=float(stats.get('Step Time(Min)', 0)), # <--- Convert here
    avg_voltage=float(stats.get('Discharge Mid Volt(V)', 0)), # <--- Convert here
    status=status
)
    
    pack.final_status = f"TESTED_{status}"
    db.add(test_result)
    db.commit()

    return {
        "battery_id": battery_id,
        "final_status": status,
        "measured_ah": measured_cap,
        "target_ah": template.target_capacity_ah,
        "energy_wh": stats.get('Discharge Energy(Wh)')
    }

@router.post("/register-bms")
def register_bms(bms_id: str, bms_model: str, db: Session = Depends(get_db)):
    """
    Adds a new BMS unit to the factory inventory.
    """
    # 1. Check if BMS already exists
    existing = db.query(BMSInventory).filter_by(bms_id=bms_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="BMS ID already exists in inventory")

    # 2. Create new BMS entry
    new_bms = BMSInventory(
        bms_id=bms_id,
        bms_model=bms_model,
        is_used=False
    )
    db.add(new_bms)
    db.commit()
    return {"status": "Success", "message": f"BMS {bms_id} ({bms_model}) registered successfully"}


@router.post("/{battery_id}/mount-bms/{bms_id}")
def mount_bms(battery_id: str, bms_id: str, db: Session = Depends(get_db)):
    """
    Links a physical BMS unit to a specific Battery Pack.
    """
    # 1. Verify Battery and BMS exist
    pack = db.query(BatteryPack).filter_by(battery_id=battery_id).first()
    bms = db.query(BMSInventory).filter_by(bms_id=bms_id).first()
    
    if not pack:
        raise HTTPException(status_code=404, detail="Battery Pack not found")
    if not bms:
        raise HTTPException(status_code=404, detail="BMS not found in inventory. Please register it first.")
    
    # 2. Logic Guards
    if bms.is_used:
        raise HTTPException(status_code=400, detail="This BMS is already assigned to another pack")
    if pack.bms_id:
        raise HTTPException(status_code=400, detail=f"This pack already has a BMS mounted: {pack.bms_id}")

    # 3. Perform the Link (Locking the BMS)
    pack.bms_id = bms_id
    bms.is_used = True
    
    db.commit()
    return {
        "status": "Success", 
        "message": f"BMS {bms_id} successfully mounted to {battery_id}",
        "bms_model": bms.bms_model
    }
import io
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.battery import BatteryPack, PDIChecklist

# --- PDI PARSING UTILITY ---
def parse_pdi_excel(file_content):
    df = pd.read_excel(io.BytesIO(file_content))
    
    def check_status(checkpoint_name):
        # Case-insensitive search for the checkpoint in the Excel
        row = df[df['Checkpoint'].str.contains(checkpoint_name, case=False, na=False)]
        if not row.empty:
            val = str(row.iloc[0]['Status']).strip().lower()
            return val in ['pass', 'ok', 'yes', 'true', '1']
        return False

    # Extract OCV value
    ocv_row = df[df['Checkpoint'].str.contains('OCV', case=False, na=False)]
    ocv_val = float(ocv_row.iloc[0]['Status']) if not ocv_row.empty else 0.0

    return {
        "visual_finish_ok": check_status("Visual"),
        "terminal_tightness_ok": check_status("Terminal"),
        "internal_wiring_routing_ok": check_status("Wiring"),
        "handle_secure_ok": check_status("Handle"),
        "sticker_labeling_ok": check_status("Label"),
        "bms_communication_ok": check_status("BMS"),
        "short_circuit_test_ok": check_status("Short"),
        "final_ocv_v": ocv_val,
        "polarity_check_ok": check_status("Polarity"),
        "warranty_seal_applied": check_status("Warranty"),
        "accessories_included": check_status("Accessories")
    }

# --- ENDPOINT ---
@router.post("/{battery_id}/upload-pdi")
async def upload_pdi_checklist(
    battery_id: str, 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    # 1. Read file and Parse
    content = await file.read()
    try:
        results = parse_pdi_excel(content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Checklist parsing failed: {str(e)}")

    # 2. Logic: Must pass all booleans for a final 'PASS'
    # Check if any boolean field is False
    failed_checkpoints = [k for k, v in results.items() if isinstance(v, bool) and v is False]
    verdict = "PASS" if not failed_checkpoints else "FAIL"

    # 3. Save PDI Record
    new_pdi = PDIChecklist(
        battery_id=battery_id,
        **results,
        inspector_name="Factory_Admin",
        final_result=verdict
    )
    
    # 4. Update Battery Pack Master Status
    pack = db.query(BatteryPack).filter_by(battery_id=battery_id).first()
    if pack:
        pack.final_status = "READY_FOR_DISPATCH" if verdict == "PASS" else "PDI_REJECTED"

    db.add(new_pdi)
    db.commit()

    return {
        "battery_id": battery_id,
        "pdi_status": verdict,
        "failed_points": failed_checkpoints if verdict == "FAIL" else None,
        "final_ocv": results['final_ocv_v']
    }