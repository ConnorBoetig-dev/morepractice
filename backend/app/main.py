# app/main.py

from fastapi import FastAPI
from app.db.base import Base
from app.db.session import engine

# 👇 import ALL models here so SQLAlchemy sees them before create_all
from app.models.user import User, UserProfile
from app.models.question import Question

# create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Billings API")

# routers
from app.api.v1.auth_routes import router as auth_router
app.include_router(auth_router, prefix="/api/v1")
