from fastapi import APIRouter

from app.api.routes import health, tags, todos

api_router = APIRouter(prefix="/api")
api_router.include_router(health.router)
api_router.include_router(todos.router)
api_router.include_router(tags.router)
