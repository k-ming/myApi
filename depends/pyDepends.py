from typing import Union
from fastapi import Depends, APIRouter, Cookie
from fastapi.params import Header
from fastapi.exceptions import HTTPException

router1 = APIRouter(
    tags=["依赖注入"],
    prefix="/pyDepends",
)

def common_parameters(q:Union[str,None] = None, skip: int = 0, limit: int = 100):
    return {"skip": skip, "limit": limit, "q": q}

@router1.get("/dep_func", name="函数作为依赖")
async def read_params(commons: dict = Depends(common_parameters)):
    """
    - 普通函数作为依赖
    - **commons**: 注入的依赖 common_parameters
    """
    return commons

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

class CommonQueryParams():
    def __init__(self, q:Union[str,None] = None, skip: int = 0, limit: int = 100):
        self.q = q
        self.skip = skip
        self.limit = limit

@router1.get("/dep_class", name="类作为依赖")
async def read_params(commons: CommonQueryParams = Depends()):
    """
    - 使用类作为依赖
    - **commons**: 注入的依赖 CommonQueryParams 是一个类
    """
    response = {}
    if commons.q:
        response.update({"q": commons.q})
    items = fake_items_db[commons.skip : commons.skip + commons.limit]
    response.update({"items": items})
    return response


def query_extractor(q:Union[str,None] = None):
    return q

def query_or_cookie_extractor(
        q:str = Depends(query_extractor),
        last_query:Union[str,None] = Cookie(default=None) ):
    if not q:
        return last_query
    return q

@router1.get("/dep_sub", name="多重依赖，子依赖")
async def read_params(query_or_default: query_or_cookie_extractor=Depends()):
    """
    - **query_or_default**: 多重依赖，子依赖
    """
    return {"query_or_default": query_or_default}


def pre_depends():
    print("pre_depends, no return !")

def verify_token(x_token:str = Header()):
    if x_token != "x-token":
        raise HTTPException(status_code=400, detail="token is invalid!")
    return x_token

@router1.get("/dep_decorator", dependencies=[Depends(pre_depends), Depends(verify_token)], name="装饰器中添加多个依赖，依赖项可以没有返回值")
async def read_params():
    """
    - **路径装饰器依赖:** 被依赖的函数可以raise 异常，可以return返回值值，但是被装饰的方法无法使用返回值
    """
    return {"items": fake_items_db}