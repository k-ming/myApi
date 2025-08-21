from fastapi import APIRouter, HTTPException
from datetime import datetime
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder

"""
1、三种参数：路径参数、查询参数、请求体
2、查询参数和字符串校验
3、路径参数和字符串校验
"""

router = APIRouter(
    prefix="/items",
    tags=["参数"],
    responses={404: {"description": "Not found"}},
)

fake_items_db = {"plumbus": {"name": "Plumbus"}, "gun": {"name": "Portal Gun"}}


@router.get("/{item_id}", deprecated=True, name="路径参数")
async def read_item(item_id: str):
    """
    - "item_id" read item by item_id
    - "deprecated" 废弃的API标记
    """
    if item_id not in fake_items_db:
        raise HTTPException(status_code=404, detail="Item not found", headers={"X-Error": "There goes my error"})
    return {"name": fake_items_db[item_id]["name"], "item_id": item_id}


@router.put("/{item_id}",
            responses={403: {"description": "operation is forbidden"}},
            # status_code=status.HTTP_403_FORBIDDEN
            summary="查询参数",
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
    return {"item_id": item_id, "name": "The great Plumbus"}


book_db = {}


class Books(BaseModel):
    title: str
    description: str | None = None
    timestamp: datetime
    tax: float = 10.5
    tags: list[str] = []


books = {
    "lx": {"title": "呐喊", "description": "呐喊", "tax": 62, },
    "ls": {"title": "茶馆", "description": None, "tax": 50.2, "tags": []},
}


@router.post("/create_book", name="请求体")
def create_book(id: str, item: Books):
    """
    - **fake_db** 只能接受与json兼容的数据
    - **jsonable_encoder** 可以将与json不兼容的时间格式数据转化成字符串格式
    """
    json_compatibler_item_data = jsonable_encoder(item)
    book_db[id] = json_compatibler_item_data
    return book_db


router2 = APIRouter(
    prefix="/paramVerify",
    tags=['查询参数和字符串校验']
)
from typing import Union, List, Optional, Annotated
from fastapi import Query


@router2.get("/book1/", name="可选参数类型与默认值",)
async def read_book1(q: str | None = None):
    """
    - param q: 字符串类型，非必填，默认值None
    """
    if q:
        return book_db.update({"q": q})
    return books

@router2.get("/book2/", name="参数的条件约束Query")
async def read_book2(q: Union[str, None] = Query(max_length=5, min_length=1)):
    """
    - param q: 使用FastAPI.Query 设置默认值，约束条件，[最大长度5, 最小长度1, 在部分FastAPI版本中不生效]
    """
    if q:
        book_db.update({"q": q})
        return book_db
    return books

@router2.get("book2_1", name="Annotated注解中的条件约束")
async def read_book2_1(q: Annotated[Union[str, None], Query(max_length=5, min_length=1)] = None):
    if q:
        book_db.update({"q": q})
        return book_db
    return books

@router2.get("/book3/", name="参数Query约束中使用正则pattern")
async def read_book3(author: Union[str, None] = Query(default=None, pattern="^ls$"),):
    """
    - param author: Query使用pattern关键字约束 author的开头和结尾，限制为ls
    """
    if author:
        return books.get(author)
    return books

@router2.get("/book4", name="查询参数支持列表")
async def read_book4(author: Union[List[str], None]):
    """
    - param author: 查询参数支持一组列表数据，使用Union[List[str], None] 或者 Union[list, None]
    """
    if author:
        return author
    return books

@router2.get("/book4_1", name="使用list参数")
async def read_book4_1(author: Optional[list]):
    """
    - param author: 使用list 也可以表示入参为列表类型
    """
    if author:
        return author
    return books

@router2.get("/book5", name="Query的元数据")
async def read_book5(q: Optional[str] = Query(title='标题', alias="author", description="Query元数据的使用", deprecated=True)):
    if q:
        return books.get(q)
    return books

router3 = APIRouter(
    prefix="/pathParamVerify",
    tags=['路径参数与数值校验']
)

from fastapi import Path

@router3.get("/{item_id}", name="Path的数值校验")
def read_item(item_id: Annotated[Optional[int], Path(..., ge=2, le=10)]) -> dict:
    """
    - param item_id: Path约束与Query类似，主要是对数值型数据做验证
    """
    if item_id:
        return {"item_id": item_id}
    return {"msg":"nothing!"}

@router3.get("/get_price/", name="浮点类型的数值校验")
async def get_price(price: float = Query(gt=0, lt=100.0)):
    if price:
        return {"price": price}
    return {"msg": "nothing!"}

@router3.get("/item1/{item_id}", name="路径参数与查询参数的排序")
def read_item(item_id: str, q:str):
    if q:
        return {"item_id": item_id}
    return {"msg":"nothing!"}

@router3.get("/item2/{item_id}", name="Path约束的元数据")
def read_item(item_id: int = Path(title="标题", description="Path约束的元数据", deprecated=True)):
    if item_id:
        return {"item_id": item_id}
    return {"msg":"nothing!"}

@router3.post("/create_item", name="python中位置参数、关键字参数的使用,*以后的表示关键字参数")
async def create_item(item_id: int, *,  name: str):
    return {"item_id": item_id, "name": name}
