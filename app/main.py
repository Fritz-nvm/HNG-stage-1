from fastapi import FastAPI
from app.api.routes import string_router

app = FastAPI(
    title="Scalable String API",
    description="A demonstration of a clean architecture structure using services and models.",
    version="1.0.0",
)

app.include_router(string_router)

@app.get("/", include_in_schema=False)
def read_root():
    return {"message": "Welcome to the String Analysis API."}
