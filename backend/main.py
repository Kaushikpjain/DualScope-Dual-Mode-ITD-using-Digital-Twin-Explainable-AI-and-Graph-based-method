from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import api

app = FastAPI(title="Insider Threat Detection API")

# Configure CORS for the frontend dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for development
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(api.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Insider Threat System API is running"}
