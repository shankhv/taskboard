import logging
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from app.database import connect_to_mongo, close_mongo_connection
from app.controllers import task_controller, category_controller, tag_controller

# -------------------- Logging Configuration --------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("taskboard_app")

# -------------------- Lifespan Management --------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info("Starting up TaskBoard API...")
        await connect_to_mongo()
        logger.info("Connected to MongoDB successfully.")
        yield
    except Exception as e:
        logger.exception(f"Error during startup: {e}")
        raise
    finally:
        logger.info("Shutting down TaskBoard API...")
        await close_mongo_connection()
        logger.info("MongoDB connection closed.")

# -------------------- FastAPI Application --------------------
app = FastAPI(
    title="TaskBoard API",
    description="FastAPI TaskBoard with Clean Architecture",
    version="1.0.0",
    lifespan=lifespan
)

# -------------------- Middleware for Request Logging --------------------
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code} for {request.method} {request.url.path}")
    return response

# -------------------- Routers --------------------
logger.info("Registering API routers...")
app.include_router(task_controller.router)
app.include_router(category_controller.router)
app.include_router(tag_controller.router)
logger.info("Routers registered successfully.")

# -------------------- Routes --------------------
@app.get("/")
async def root():
    logger.info("Root endpoint accessed.")
    return {"message": "TaskBoard API is running"}

# -------------------- Uvicorn Entry Point --------------------
if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Uvicorn server at http://localhost:8000 ...")
    uvicorn.run(app, host="localhost", port=8000)
