from fastapi import FastAPI

subapi = FastAPI()

@subapi.get("/")
async def root():
    return {"message": "Hello subapi!"}