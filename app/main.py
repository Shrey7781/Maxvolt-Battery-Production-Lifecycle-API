from fastapi import FastAPI
from app.database import engine, Base

# 1. IMPORT YOUR ROUTERS
from app.routers import cell_router  # This looks for app/routers/cell_router.py

# 2. IMPORT ALL MODELS (Critical for SQLAlchemy to map relationships)
from app.models.cell import Cell
from app.models.battery import BatteryPack, PackTestResult
from app.models.template import BatteryTemplate
from app.models.grading import GradingStepResult

# 3. CREATE TABLES
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Maxvolt Energy Production Portal")

# 4. INCLUDE THE ROUTER
app.include_router(cell_router.router)

@app.get("/")
def home():
    return {"message": "Maxvolt Backend is Live"}