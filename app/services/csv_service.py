import pandas as pd
import io
import re
from sqlalchemy.orm import Session
from app.models.cell import Cell
from fastapi import HTTPException

class CSVService:
    @staticmethod
    def calculate_capacity_group(capacity: float) -> str:
        """
        Groups cells into 0.5 Ah buckets. 
        Example: 102.3 -> '102.0-102.5'
        """
        if capacity is None: return "Unknown"
        # Logic: Round down to the nearest 0.5
        lower_bound = (capacity * 2 // 1) / 2
        upper_bound = lower_bound + 0.5
        return f"{lower_bound:.1f}-{upper_bound:.1f} Ah"

    @staticmethod
    def parse_machine_excel(db: Session, file_content: bytes):
        try:
            excel_file = pd.ExcelFile(io.BytesIO(file_content))
            
            # --- [Step A: Metadata Search as before] ---
            df_basic = excel_file.parse('Basic data', header=None)
            cell_id, start_time_str, schedule_name = None, None, ""
            for row_idx in range(len(df_basic)):
                for col_idx in range(len(df_basic.columns)):
                    val = str(df_basic.iloc[row_idx, col_idx])
                    if "Battery code:" in val: cell_id = str(df_basic.iloc[row_idx, col_idx + 1]).strip()
                    if "Start time:" in val: start_time_str = str(df_basic.iloc[row_idx, col_idx + 1]).strip()
                    if "Work step Schedule name:" in val: schedule_name = str(df_basic.iloc[row_idx, col_idx + 1]).strip()

            # --- [Step B: Metrics Extraction] ---
            df_stat = excel_file.parse('Statistical data')
            df_stat.columns = df_stat.columns.str.strip()
            discharge_row = df_stat[df_stat['Work Step Name'].str.contains('CC-D', na=False)].iloc[0]
            ocv_row = df_stat[df_stat['Work Step Number'] == 1.0].iloc[0]

            # --- [Step C: Database Update & Grouping] ---
            cell = db.query(Cell).filter(Cell.cell_id == cell_id).first()
            if not cell:
                cell = Cell(cell_id=cell_id)
                db.add(cell)

            # 1. Store basic metrics
            cell.actual_cap_ah = float(discharge_row['Capacity(Ah)'])
            cell.ocv_volts = float(ocv_row['Open Voltage(V)'])
            
            # 2. AUTO-CALCULATE CAPACITY GROUP
            cell.capacity_group = CSVService.calculate_capacity_group(cell.actual_cap_ah)

            # 3. Parse Cycle & Time
            cycle_match = re.search(r"(\d+\.?\d*)C", schedule_name)
            if cycle_match: cell.grading_cycle = float(cycle_match.group(1))
            if start_time_str: cell.grading_date = pd.to_datetime(start_time_str)

            db.commit()
            return {
                "cell_id": cell_id,
                "capacity": cell.actual_cap_ah,
                "group": cell.capacity_group,
                "status": "Success"
            }
            
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=f"Grouping Error: {str(e)}")