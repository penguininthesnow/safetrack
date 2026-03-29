import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import Base, engine
from backend import models
# from backend.routers import users, inspections, notification_settings, osha
from backend.routers.users import router as users_router
from backend.routers.inspections import router as inspections_router
from backend.routers.notification_settings import router as notification_settings_router
from backend.routers.osha import router as osha_router


print(engine.url) #查找資料庫

app = FastAPI(
    title="SafeTrack API",

    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://www.penguinthesnow.com",
        "https://penguinthesnow.com",
        "http://www.penguinthesnow.com",
        "http://penguinthesnow.com",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 建立資料表
# Base是declarative base; Base.metadata是所有模型的資料表資訊集合; _create_all()會根據models建立資料表
Base.metadata.create_all(bind=engine)

# routers
app.include_router(users_router)
app.include_router(inspections_router)
app.include_router(notification_settings_router)
app.include_router(osha_router)

print("=== ROUTES ===")
for route in app.routes:
    print(route.path)


# debug
print("AWS_REGION =", os.getenv("AWS_REGION"))
print("S3_BUCKET_NAME =", os.getenv("S3_BUCKET_NAME"))
print("HAS ACCESS KEY =", bool(os.getenv("AWS_ACCESS_KEY_ID")))

