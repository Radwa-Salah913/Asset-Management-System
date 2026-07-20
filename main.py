from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api import import_routes, asset_routes,ask_assets_routes,risk_routes,enrich_routes, report_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Staring the Application")
    yield
    print("End the Application")


app = FastAPI(
    lifespan=lifespan,
    title="AssetManagement",
    prefix="/api/v1",
    tags=["api"]
)
 
@app.get("/")
async def root():
    return { "message" : "Welcome to Asset Management"}


app.include_router(import_routes.router)
app.include_router(asset_routes.router)
app.include_router(ask_assets_routes.router)
app.include_router(risk_routes.router)
app.include_router(enrich_routes.router)
app.include_router(report_routes.router)