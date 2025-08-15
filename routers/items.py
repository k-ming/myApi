import inspect

from fastapi import APIRouter, Depends,HTTPException, status
from ..dependencies import get_token_header
import os, sys
from datetime import datetime
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder

router = APIRouter(
    prefix="/items",
    tags=["参数"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)

fake_items_db = {"plumbus": {"name": "Plumbus"}, "gun": {"name": "Portal Gun"}}

@router.get("/")
async def read_items():
    return fake_items_db

@router.get("/{item_id}", deprecated=True, name="路径参数")
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
            name="查询参数"
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
    tax: float = 10.5
    tags: list[str] = []

books = {
    "lx": {"title": "呐喊", "description": "呐喊", "tax": 62, },
    "ls": {"title": "茶馆", "description": None, "tax": 50.2,  "tags": []},
}

@router.post("/create_book", tags=["items"])
def create_book(id: str, item: Books):
    """
    - **fake_db** 只能接受与json兼容的数据
    - **jsonable_encoder** 可以将与json不兼容的时间格式数据转化成字符串格式
    """
    json_compatibler_item_data = jsonable_encoder(item)
    book_db[id] = json_compatibler_item_data
    return book_db

@router.patch("/boos/{id}", response_model=Books, tags=["items"], deprecated=True)
def update_book(id: str, item: Books):
    stored_book_data = books[id]
    stored_book_model = Books(**stored_book_data)
    update_data = item.dict(exclude_unset=True)
    updated_item = stored_book_model.copy(update=update_data)
    books[id] = updated_item = jsonable_encoder(updated_item)
    return updated_item

@router.put("/book/{id}", tags=["items"], response_model=Books)
def update_book(id: str, item: Books):
    """
    - **des**: 使用部分更新时，如果没有传值的，将会会被默认值覆盖，比如 tax会被覆盖为 10.5
    - :param id: books 对象的key
    - :param item: Books模型
   - :return:
    """
    update_item_encoded = jsonable_encoder(item)
    books[id] = update_item_encoded
    return update_item_encoded