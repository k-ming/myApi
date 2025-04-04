from fastapi import APIRouter, Path, Query, Body
from pydantic import BaseModel, Field, HttpUrl
from typing import Annotated, Union
"""
多请求体
"""
router = APIRouter()


class Item(BaseModel):
    name: str
    description: str | None = Field(default=None, title="The description of the item", alias="description", max_length=300)
    price: float =Field(gt=0, title="The price of the item", alias="price", max_length=100)
    tax: float | None = None


class User(BaseModel):
    name: str
    age: int | None = None


@router.put("/items/{item_id}")
async def update_item(item_id: Annotated[int, Path(title="The ID of the item to get", ge=0, le=100)],
                      importance: Annotated[int, Body(embed=True)],
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


from typing import List, Set
from pydantic import HttpUrl

class SubPkg(BaseModel):
    url: HttpUrl  # 引入pydantic 额外的类型
    description: str | None = None

class Package(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tax: Union[float, None] = None
    tags: Set[str]
    sub: List[SubPkg] | None = None  #嵌套模型

@router.put("/pkgs/{pkg_id}")
def update_package(pkg_id: int ,package: Package) -> dict[str, int | Package]:
    """
    :param pkg_id:包ID \n
    :param package: tags 属性带有子类型 List[], 进一步设置成去重复的set类型
    :return:
    """
    return {"pkg_id":pkg_id, "package": package}


class DeepPackage(BaseModel):
    name: str
    description: str | None = None
    pkgs: Package | None = None # 任意深度的模型嵌套

@router.put("/deepfakes/{pkg_id}")
def create_deep_package(pkg_id: int ,deep: list[DeepPackage] ) -> dict[str, int | list[DeepPackage]]:
    """
    :param pkg_id: pkg_id \n
    :param deep: 纯列表请求体, list[model] \n
    :return: dict[str, int | list[DeepPackage]]
    """
    return {"pkg_id":pkg_id, "deep": deep}

