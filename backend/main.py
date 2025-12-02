from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from backend.data.database import create_db_and_tables, add_data
from backend.routers.router import router

app = FastAPI(
    title="Paralympics Data API",
    description="API to serve Paralympics data for analysis",
    version="1.0.0"
)

# CORS Configuration
# This is crucial to allow your frontend (running on a different port) to fetch data from this backend.
origins = [
    "http://localhost:8000",
    "*"                       # Allow all for development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the router defined in router.py
app.include_router(router)

@app.on_event("startup")
def on_startup():
    """Check database connection on startup"""
    create_db_and_tables()
    # add_data() # Uncomment only if database is empty

@app.get("/")
def root():
    return {"message": "Backend API is running."}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)