from fastapi import HTTPException, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

subApp1 = FastAPI(
    prefix="/exception",
    tags=["异常处理"]
)

origins = {
    "http://127.0.0.1:8099",
}
subApp1.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = {
    "Lily":{"name":"Lily", "age":35, "email":"Lily366@163.com"},
    "Piter":{"name":"Piter", "age":32, "tags":["bright", "happy"]},
    "Join":{"name":"Join", "age":40, "create_at":datetime.now()},
}

@subApp1.get("/get_name", name="HTTPException异常抛出")
async def get_name(name : str):
    if name in db:
        return db[name]
    raise HTTPException(status_code=404, detail="name not found!", headers={"X-Error":"There goes my error"})


class UnicornException(Exception): # 自定义异常
    def __init__(self, name:str):
        self.name = name

@subApp1.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return JSONResponse(
        status_code=418,
        content={"message": f"{exc.name} Unicorn exception occurred!"},
    )

@subApp1.get("/get_exception", name="使用exception_handler添加自定义异常")
async def get_exception(name: str):
    if name in db:
        return db[name]
    raise UnicornException(name)

@subApp1.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )

class Item(BaseModel):
    title: str
    size: int

@subApp1.post("/items", name="使用 RequestValidationError 的请求体")
async def create_item(item: Item):
    return item


