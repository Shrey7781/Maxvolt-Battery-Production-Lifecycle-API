from fastapi import FastAPI
from app.database import engine, Base

# 1. IMPORT ALL MODELS FIRST (Must be before create_all)
from app.models.cell import Cell
from app.models.template import BatteryTemplate 
from app.models.battery import BatteryPack, PackTestResult
from app.models.grading import GradingStepResult

# 2. IMPORT ROUTERS
from app.routers import cell_router, template_router, battery_router

# 3. CREATE TABLES
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Maxvolt Energy Production Portal")

# 4. INCLUDE ROUTERS
app.include_router(cell_router.router)
app.include_router(template_router.router)
app.include_router(battery_router.router)

@app.get("/")
def home():
    return {"message": "Maxvolt Backend is Live"}