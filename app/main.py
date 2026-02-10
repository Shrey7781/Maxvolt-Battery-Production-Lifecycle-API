from fastapi import FastAPI
from app.database import engine
from app.models import *

app = FastAPI(title="Maxvolt Battery Lifecycle API")

@app.get("/")
def health_check():
    return {"status": "Backend Running"}
