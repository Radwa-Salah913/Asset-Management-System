from fastapi import FastAPI
from app.api import import_routes, asset_routes

app = FastAPI()

app.include_router(import_routes.router)
app.include_router(asset_routes.router)