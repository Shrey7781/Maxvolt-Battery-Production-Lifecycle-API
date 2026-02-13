from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # Missing import
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

# 4. ADD CORS MIDDLEWARE (MUST be before including routers)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, change this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # This enables OPTIONS, POST, GET, etc.
    allow_headers=["*"],
)

# 5. INCLUDE ROUTERS
# Note: Ensure the 'prefix' in your routers matches what the frontend calls.
# If cell_router has prefix="/cells", then calling /cells will work.
app.include_router(cell_router.router)
app.include_router(template_router.router)
app.include_router(battery_router.router)

@app.get("/")
def home():
    return {"message": "Maxvolt Backend is Live"}