import inspect

from fastapi import APIRouter, Depends,HTTPException, status
from ..dependencies import get_token_header
import os, sys
from datetime import datetime
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder

router = APIRouter(
    prefix="/items",
    tags=["items"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)

fake_items_db = {"plumbus": {"name": "Plumbus"}, "gun": {"name": "Portal Gun"}}

@router.get("/")
async def read_items():
    return fake_items_db

@router.get("/{item_id}", deprecated=True)
async def read_item(item_id: str):
    """
    - "item_id" read item by item_id
    - "deprecated" 启用的API标记
    """
    if item_id not in fake_items_db:
        raise HTTPException(status_code=404, detail="Item not found", headers={"X-Error":"There goes my error"})
    return {"name":fake_items_db[item_id]["name"], "item_id":item_id}

@router.put("/{item_id}",
            tags=["items_extra"],
            responses={403: {"description": "operation is forbidden"}},
            # status_code=status.HTTP_403_FORBIDDEN
            summary="Update an item",
            # description="update an item with a item_id",
            response_description="updated item response",
            )
async def update_item(item_id: str):
    """
    - 在items module中的子方法单独定义了 tags, 不会覆盖module的域 items，会单独生成 items_extra 域
    - **param**: item_id 必须为 plumbus
    - **status_code** 状态码在响应中使用，并会被添加到 OpenAPI 概图
    - **summary** 给请求添加 summary
    - **description** 给请求添加 description ， 添加了description 会覆盖当前添加吗的描述
    - **response_description** 给响应添加 descript
    """
    if item_id != "plumbus":
        raise HTTPException(status_code=403, detail="you can only update plumbus")
    return {"item_id":item_id, "name":"The great Plumbus"}

book_db = {}

class Books(BaseModel):
    title: str
    description: str | None = None
    timestamp: datetime

@router.post("/create_book", tags=["items"])
def create_book(id: str, item: Books):
    """
    - **fake_db** 只能接受与json兼容的数据
    - **jsonable_encoder** 可以将与json不兼容的时间格式数据转化成字符串格式
    """
    json_compatibler_item_data = jsonable_encoder(item)
    book_db[id] = json_compatibler_item_data
    return book_db