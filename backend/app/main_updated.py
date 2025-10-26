from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from pathlib import Path

from . import payments
from . import partnerships

app = FastAPI(title="2D to 3D Converter with Partnership System", version="2.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(payments.router)
app.include_router(partnerships.router)

@app.get("/")
async def root():
    return {
        "message": "2D to 3D Converter with Partnership System", 
        "version": "2.0.0",
        "features": [
            "Image to 3D conversion",
            "Revenue sharing partnerships",
            "License management",
            "Payment processing"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
