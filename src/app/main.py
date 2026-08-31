from fastapi import FastAPI

from app.api.v1.routes.properties import router as property_router


app = FastAPI(
    title="Property Dealer AI",
    description="AI-powered property management and search API",
    version="1.0.0",
)


app.include_router(
    property_router,
    prefix="/api/v1",
)