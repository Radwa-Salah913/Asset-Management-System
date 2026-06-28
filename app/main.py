from fastapi import FastAPI
from app.api import import_routes, asset_routes,ask_routes,risk_routes,enrich_routes, report_routes

app = FastAPI()

app.include_router(import_routes.router)
app.include_router(asset_routes.router)
app.include_router(ask_routes.router)
app.include_router(risk_routes.router)
app.include_router(enrich_routes.router)
app.include_router(report_routes.router)