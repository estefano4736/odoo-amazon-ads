import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.api.auth import router as auth_router
from app.api.campaigns import router as campaigns_router
from app.api.bulk import router as bulk_router
from app.core.db import db

app = FastAPI(
    title="Amazon Ads Optimization Engine (AAOE)",
    description="Automated PPC bidding, budget shifts, and negative keywords builder.",
    version="1.0.0"
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(campaigns_router)
app.include_router(bulk_router)

# Mount Static Files
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Rules update payload model
class RulesPayload(BaseModel):
    target_acos: float
    max_spend_no_sales: float
    min_clicks_no_sales: int
    smoothing_factor: float
    min_bid: float
    max_bid: float
    budget_transfer_pct: float

# Routes
@app.get("/", response_class=HTMLResponse)
def read_root():
    """Serves the main Dashboard single-page application."""
    index_file = os.path.join(static_dir, "index.html")
    if not os.path.exists(index_file):
        return HTMLResponse(
            content="<html><body><h1>AAOE Server Running</h1><p>Static dashboard files not created yet.</p></body></html>",
            status_code=200
        )
    with open(index_file, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read(), status_code=200)

@app.get("/api/rules")
def get_rules():
    """Retrieves current rules and thresholds configuration."""
    return db.get_rules()

@app.post("/api/rules")
def update_rules(payload: RulesPayload):
    """Updates optimization rules and returns the new configuration."""
    updated = db.update_rules(
        target_acos=payload.target_acos,
        max_spend=payload.max_spend_no_sales,
        min_clicks=payload.min_clicks_no_sales,
        smoothing=payload.smoothing_factor,
        min_bid=payload.min_bid,
        max_bid=payload.max_bid,
        budget_transfer=payload.budget_transfer_pct
    )
    return {
        "status": "success",
        "message": "Optimization rules updated successfully.",
        "rules": updated
    }

@app.get("/api/history")
def get_history():
    """Retrieves the history of all optimization runs."""
    return db.get_history()

@app.on_event("startup")
async def startup_event():
    """Starts background services (like the Downloads folder monitor)."""
    try:
        from app.core.watcher import watch_downloads_loop
        import asyncio
        asyncio.create_task(watch_downloads_loop())
        print("[OK] Background Downloads watcher started successfully!")
    except Exception as err:
        print(f"[ERROR] Failed to start background Downloads watcher: {err}")
