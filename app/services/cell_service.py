import pandas as pd
import io
from sqlalchemy.orm import Session
from app.models.cell import Cell
from fastapi import HTTPException
from datetime import datetime

class CellService:
    @staticmethod
    def calculate_capacity_group(capacity: float) -> str:
        """Groups cells into 0.5 Ah buckets for warehouse sorting."""
        if capacity is None: return "Unknown"
        lower_bound = (capacity * 2 // 1) / 2
        upper_bound = lower_bound + 0.5
        return f"{lower_bound:.1f}-{upper_bound:.1f} Ah"

    @staticmethod
    async def process_grading_excel(db: Session, file_content: bytes):
        try:
            # 1. Load the Excel file to access both 'Basic' and 'Statistical' sheets
            excel_file = pd.ExcelFile(io.BytesIO(file_content))
            
            # --- [Step A: Extract Cell ID from 'Basic data'] ---
            df_basic = excel_file.parse('Basic data', header=None)
            cell_id = None
            for row_idx in range(len(df_basic)):
                for col_idx in range(len(df_basic.columns)):
                    val = str(df_basic.iloc[row_idx, col_idx])
                    if "Battery code:" in val:
                        cell_id = str(df_basic.iloc[row_idx, col_idx + 1]).strip()
                        break
            
            if not cell_id or cell_id == "nan":
                raise HTTPException(status_code=400, detail="Cell ID not found in Basic data sheet")

            # --- [Step B: Extract Metrics from 'Statistical data'] ---
            df_stat = excel_file.parse('Statistical data')
            df_stat.columns = df_stat.columns.str.strip()

            # Locate Step 3.0 (CC-D) which contains the 3.39V OCV and 2.492V Cutoff
            cc_d_rows = df_stat[df_stat['Work Step Number'] == 3.0]
            if cc_d_rows.empty:
                # Fallback to name search if the step number is different
                cc_d_rows = df_stat[df_stat['Work Step Name'].str.contains('CC-D', na=False, case=False)]

            if cc_d_rows.empty:
                raise HTTPException(status_code=400, detail=f"Discharge step (CC-D) not found for Cell {cell_id}")
            
            data_row = cc_d_rows.iloc[0]

            # --- [Step C: Database Update] ---
            # Search for the cell; if it doesn't exist, we create a new record
            cell = db.query(Cell).filter(Cell.cell_id == cell_id).first()
            if not cell:
                cell = Cell(cell_id=cell_id, is_used=False)
                db.add(cell)

            # Capture High-Precision Metrics
            cell.actual_cap_ah = float(data_row.get('Capacity(Ah)', 0))
            cell.ocv_volts = float(data_row.get('Open Voltage(V)', 0))
            
            # Fuzzy Column Search for Cut-off (handles the double-space 'Cut-off  Voltage(V)')
            cutoff_col = [c for c in df_stat.columns if "Cut-off" in c and "Voltage" in c]
            if cutoff_col:
                cell.cut_off_voltage = float(data_row[cutoff_col[0]])
            else:
                cell.cut_off_voltage = 0.0

            # Calculate the bin/group for assembly
            cell.capacity_group = CellService.calculate_capacity_group(cell.actual_cap_ah)
            cell.grading_date = datetime.now()

            db.commit()

            return {
                "status": "Success",
                "cell_id": cell_id,
                "data": {
                    "capacity": float(cell.actual_cap_ah),
                    "ocv": float(cell.ocv_volts),
                    "cutoff": float(cell.cut_off_voltage),
                    "group": cell.capacity_group
                }
            }
            
        except Exception as e:
            db.rollback()
            # Clean logging for debugging production issues
            print(f"Grading Error for {cell_id if 'cell_id' in locals() else 'Unknown'}: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Grading Error: {str(e)}")