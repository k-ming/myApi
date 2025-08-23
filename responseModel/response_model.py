from typing import List

from  fastapi import APIRouter, Form
from pydantic import BaseModel

router1 = APIRouter(
    prefix="/responseModel",
    tags=["响应模型和默认值"]
)


class UserIn(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    username: str

class Goods(BaseModel):
    name: str
    description: str | None ="a pretty gift !"
    price: float = 10.5
    tags: list[str] | None = None


gifts = {
    "cat":{"name":"cat", "price":0.0},
    "dog":{"name":"dog", "price":30.5, "tags":["pretty", "little"]},
    "polly":{"name":"cat", "price":11.2, "description":"a bird name's"},
}

@router1.post("/register", name="响应模型", response_model=UserOut )
async def register(user_in: UserIn = Form()):
    return UserOut(**user_in.model_dump()) # 将字典 user_in.model_dump() 解包后传给 UserOUT

@router1.post("/create_good", name="响应模型默认值", response_model=Goods )
async def create_good(name: str):
    return gifts.get(name)

@router1.get("/get_goods/{name}", name="响应模型不使用默认值", response_model=Goods, response_model_exclude_none=True)
async def get_good(name: str):
    return gifts.get(name)

@router1.get("/include", name="响应模型只包含模型指定的属性", response_model=Goods, response_model_include=["name", "tags"])
async def include(name: str):
    return gifts.get(name)

@router1.get("/exclude", name="响应模型排除指定的属性", response_model=Goods, response_model_exclude=["tags", "description"])
async def exclude(name: str):
    return gifts.get(name)
