from fastapi import FastAPI
from app.database import engine, Base
import app.models.user
import app.models.record
from app.routers import auth, records, dashboard, users

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Finance Backend")

app.include_router(auth.router, prefix="/api")
app.include_router(records.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(users.router, prefix="/api")

@app.get("/")
def home():
    return {"message": "Finance Backend Running"}