from fastapi import APIRouter, Path, Query, Body
from pydantic import BaseModel, Field, HttpUrl
from typing import Annotated, Union
"""
请求体-多个参数
"""
router1 = APIRouter(
    prefix="/requestBody",
    tags=["请求体-多参数-字段"]
)

class Item(BaseModel):
    name: str
    description: str | None = Field(default=None, title="The description of the item", alias="description", max_length=300)
    price: float = Field(gt=10, title="The price of the item", alias="price", le=100)
    tax: float | None = None

class User(BaseModel):
    name: str
    age: int | None = None

@router1.put("/items1/{item_id}", name="混合使用路径参数、查询参数、请求体")
async def update_item(item_id: Annotated[int, Path(title="The ID of the item to get", ge=0, le=100)],
                      q: str = None,
                      item: Item | None = None,
                      user: User | None = None,
                      ):
    """
    - param item_id: 路径参数，特殊类型注解指定范围
    - param q: 可选查询参数
    - param item: 请求体参数
    - param user: 请求体参数，当有多个请求体参数时，json中会包含请求体键名
    """
    result = {"item_id": item_id}
    if q:
        result.update({"q": q})
    if item:
        result.update({"item": item})
    if user:
        result.update({"user": user})
    return result

@router1.get("/items/{item_id}", name="将查询参数标记请求体")
async def get_item(item_id: Annotated[int, Path(title="The ID of the item to get")],
                   importance: Annotated[int, Body()],
                   item: Item | None = None,):
    result = {"item_id": item_id}
    result.update({"importance": importance})
    if item:
        result.update({"item": item})
    return result

@router1.post("/items_1", name="使用参数名作为单个请求体的键名")
async def create_item(item: Item=Body(embed=True)):
    return item

@router1.post("/items_2", name="Body约束的元数据和模型中Field约束")
async def create_item(
        importance: Annotated[int, Body(title="title", ge=0, le=100, alias="importance", description="The importance of the item")],
        item: Item=Body()):
    result = {}
    if importance:
        result.update({"item": item})
        result.update({"importance": importance})
    return result

router2 = APIRouter(
    prefix="/modelNesting",
    tags=["请求体-嵌套"]
)
from typing import List, Set
from pydantic import HttpUrl

class ItemModel(BaseModel):
    name: str
    description: str | None = None
    tags: List[str] = None

class MarkModel(BaseModel):
    name: str
    tags: list = []

class DistinctModel(BaseModel):
    name: str
    tags: Set[str] = set()

class SetModel(BaseModel):
    name: str
    tags: set = set()

class Pkg(BaseModel):
    url: HttpUrl  # 引入pydantic 额外的类型
    description: str | None = "url 字段设置Pedantic.HttpUrl，实现输入校验"

class NestingModel(BaseModel):
    name: str | None = "parent字段嵌套Pkg模型"
    description: str | None = None
    parent: Pkg = None

class SubPkg(BaseModel):
    name: str
    description: Union[str, None] = "parent字段嵌套的Pkg类型是一个模型列表"
    parent: List[Pkg] | None = None  #嵌套模型

class DeepNesting(BaseModel):
    name: str
    description: str | None = "模型可以任意深度的嵌套"
    pkgs: SubPkg | None = None

@router2.post("/items/{item_id}", name="模型字段中嵌套List[str]")
async def create_item(item_id: Annotated[int, Path(title="The ID of the item to get")],
                   item:ItemModel):
    result = {"item_id": item_id}
    result.update({"item": item})
    return result

@router2.put("/items/{item_id}", name="模型字段中嵌套list,不指定类型")
async def update_item(item_id: Annotated[int, Path(title="The ID of the item to get")],
                      item: MarkModel):
    result = {"item_id": item_id}
    result.update({"item": item})
    return result

@router2.patch("/items/{item_id}", name="模型字段中嵌套Set类型，实现去重复")
async def update_item(item: DistinctModel):
    return item

@router2.post("/tags", name="模型的字段设置为原生集合类型，实现去重复")
async def create_item(item: SetModel):
    return item

@router2.put("/pkgs/{pkg_id}", name="模型字段定义为Pydantic的HttpUrl")
def update_package(pkg_id: int ,package: Pkg) -> dict[str, int | Pkg]:
    return {"pkg_id":pkg_id, "package": package}


@router2.post("/pkgs/create", name="模型字段中嵌套模型")
async def create_item(item: NestingModel):
    return item

@router2.post("/pkgs/list", name="模型字段中嵌套模型列表")
async def list_packages(item: SubPkg):
    return item

@router2.put("/deepfakes/{pkg_id}", name="模型可以嵌套任意深度的模型")
def create_deep_package(pkg_id: int ,deep: DeepNesting ) -> dict[str, int | DeepNesting]:
    return {"pkg_id":pkg_id, "deep": deep}

@router2.post("/nestingList",name="模型定义为纯列表类型的请求体")
async def create_item(item: List[Pkg]):
    return item

@router2.post("/dictBody", name="构建任意dict请求体")
async def create_item(item: dict[int, float], tags: dict[float,str]):
    result = {"item": item, "tags": tags}
    return result
