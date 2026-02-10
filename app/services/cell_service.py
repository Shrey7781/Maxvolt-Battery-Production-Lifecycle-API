import pandas as pd
import io
from sqlalchemy.orm import Session
from app.models.cell import Cell
from fastapi import HTTPException

class CellService:
    @staticmethod
    async def process_grading_csv(db: Session, file_content: bytes, cell_id: str):
        try:
            # Read the bytes into a pandas DataFrame
            df = pd.read_csv(io.BytesIO(file_content))

            # Logic for your 'Statistical data.csv':
            # Step 3.0 is usually the CC-D (Discharge) step where capacity is measured
            discharge_row = df[df['Work Step Name'] == 'CC-D'].iloc[0]
            
            # Step 1.0 is the first Rest/Charge where OCV is usually recorded
            ocv_row = df[df['Work Step Number'] == 1.0].iloc[0]

            db_cell = db.query(Cell).filter(Cell.cell_id == cell_id).first()
            if not db_cell:
                raise HTTPException(status_code=404, detail="Cell barcode not registered.")

            # Update the model with machine data
            db_cell.actual_cap_ah = float(discharge_row['Capacity(Ah)'])
            db_cell.ocv_volts = float(ocv_row['Open Voltage(V)'])
            
            db.commit()
            return {"status": "Success", "cell_id": cell_id, "capacity": db_cell.actual_cap_ah}
            
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=f"Parsing Error: {str(e)}")