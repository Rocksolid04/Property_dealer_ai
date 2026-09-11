from fastapi import FastAPI

from app.api.v1.routes.properties import router as property_router
from app.api.v1.routes.user import router as user_router
from app.api.v1.routes.auth import router as auth_router
from app.api.v1.routes.favorite import router as favorites_router
from app.api.v1.routes.inquiry import router as inquiry_router

app = FastAPI(
    title="Property Dealer AI",
    description="AI-powered property management and search API",
    version="1.0.0",
)


app.include_router(
    property_router,
    prefix="/api/v1",
)

app.include_router(
    user_router,
    prefix="/api/v1",
)

app.include_router(
    auth_router,
    prefix="/api/v1",
)

app.include_router(
    favorites_router,
    prefix="/api/v1",
)

app.include_router(
    inquiry_router,
    prefix="/api/v1",
)