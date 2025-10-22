import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from fastapi import FastAPI
from api.routes import router 

app = FastAPI(
    title="String Analysis API",
    description="A RESTful API service that analyzes strings and stores their computed properties",
    version="1.0.0"
)

app.include_router(router, tags=["strings"])

@app.get("/")
async def root():
    return {"message": "String Analysis API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)