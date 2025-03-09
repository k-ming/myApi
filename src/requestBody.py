from fastapi import APIRouter, Path, Query, Body
from pydantic import BaseModel
from typing import Annotated
"""
多请求体
"""
router = APIRouter()


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


class User(BaseModel):
    name: str
    age: int | None = None


@router.put("/items/{item_id}")
async def update_item(item_id: Annotated[int, Path(title="The ID of the item to get", ge=0, le=100)],
                      importance: Annotated[int, Body()],
                      q: str = None,
                      item: Item | None = None,
                      user: User | None = None,
                      ):
    """
    :param item_id: 路径参数，特殊类型注解指定范围
    :param importance: 通过Body()方法追加到请求体
    :param q: 可选默认参数
    :param item: 请求体参数
    :param user: 请求体参数，当有多个请求体参数时，json中会包含请求体键名
    :return:
    """
    result = {"item_id": item_id}
    result.update({"importance":importance})
    if q:
        result.update({"q": q})
    if item:
        result.update({"item": item})
    if user:
        result.update({"user": user})
    return result
