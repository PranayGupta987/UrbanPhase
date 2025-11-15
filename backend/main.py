import logging
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Load .env
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# --------------------------------------------------------
# IMPORT ROUTERS
# --------------------------------------------------------
from backend.routers import status, data, simulate, predict
from backend.routers.gnn_predict import router as gnn_router

# --------------------------------------------------------
# IMPORT GNN PIPELINE
# --------------------------------------------------------
from backend.gnn_pipeline.image_features import extract_features
from backend.gnn_pipeline.model import GraphSageNet
from backend.gnn_pipeline.inference import predict_for_snapshot

# --------------------------------------------------------
# CREATE APP
# --------------------------------------------------------
app = FastAPI(
    title="UrbanPulse API",
    description="AI-Powered Sustainable City Twin API",
    version="1.0.0"
)

# --------------------------------------------------------
# CORS
# --------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------------
# STARTUP
# --------------------------------------------------------
@app.on_event("startup")
async def startup_event():
    logging.info("✓ Backend started successfully.")

# --------------------------------------------------------
# ROUTERS
# --------------------------------------------------------
app.include_router(status.router, tags=["status"])
app.include_router(data.router, prefix="/data")
app.include_router(predict.router, prefix="/predict", tags=["prediction"])
app.include_router(simulate.router, tags=["simulation"])
app.include_router(gnn_router, prefix="/api", tags=["gnn"])

# --------------------------------------------------------
# ROOT
# --------------------------------------------------------
@app.get("/")
async def root():
    return {
        "message": "Welcome to UrbanPulse API",
        "docs": "/docs",
        "version": "1.0.0"
    }
