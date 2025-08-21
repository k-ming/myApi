# fastapi 学习
## 一、 启动方式
### 1、使用 unicorn 启动
```
需要从项目最外层启动，否则会报错 ImportError: attempted relative import with no known parent package 
可参考：https://stackoverflow.com/questions/76939674/fastapi-attempted-relative-import-beyond-top-level-package
uvicorn myApi.main:app
```
### 2、使用fastapi 启动 
```shell
fastapi dev myApi/main.py  # 用于调试阶段的启动，可自动重载
fastapi run myApi/main.py  # 用于生产阶段的部署
```
### 3、在 main.py 文件中启动
```shell
if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
```
---

## 二、参数
### 1、路径参数，参数中中括号加在路径中，方法中声明
```python
from fastapi import APIRouter, HTTPException
router = APIRouter()

fake_items_db = {"plumbus": {"name": "Plumbus"}, "gun": {"name": "Portal Gun"}}

@router.get("/{item_id}", deprecated=True)
async def read_item(item_id: str):
    """
    - "item_id" read item by item_id
    - "deprecated" 启用的API标记
    """
    if item_id not in fake_items_db:
        raise HTTPException(status_code=404, detail="Item not found", headers={"X-Error":"There goes my error"})
    return {"name":fake_items_db[item_id]["name"], "item_id":item_id}
```
### 2、查询参数，参数在函数中声明，会自动解析为查询参数, 如下面的例子中，id会以?item_id=2方式被携带
```python
from fastapi import  APIRouter, HTTPException
router = APIRouter()

@router.put("/item",)
async def update_item(item_id: str):
    if item_id != "plumbus":
        raise HTTPException(status_code=403, detail="you can only update plumbus")
    return {"item_id":item_id, "name":"The great Plumbus"}
```
### 3、请求体，使用pydantic声明模型作为入参，会被自动识别并被转化成json请求体，如下面的 item
```python
from fastapi import APIRouter
from pydantic import BaseModel
from datetime import  datetime
from fastapi.encoders import jsonable_encoder

router = APIRouter()

class Books(BaseModel):
    title: str
    description: str | None = None
    timestamp: datetime
    tax: float = 10.5
    tags: list[str] = []
    
book_db = {}

@router.post("/create_book")
def create_book(id: str, item: Books):
    """
    - **fake_db** 只能接受与json兼容的数据
    - **jsonable_encoder** 可以将与json不兼容的时间格式数据转化成字符串格式
    """
    json_compatibler_item_data = jsonable_encoder(item)
    book_db[id] = json_compatibler_item_data
    return book_db
```
### 4、查询参数与字符串校验
- 可选参数与默认值, 使用 str | None = None 表示数据类型是字符串、可以为None、默认值是None
```python
router2 = APIRouter(
    prefix="/paramVerify",
    tags=['查询参数和字符串校验']
)
from typing import Union, List, Optional
from fastapi import Query
@router2.get("/book1/", name="可选参数类型与默认值",)
async def read_book1(q: str | None = None):
    """
    - param q: 字符串类型，非必填，默认值None
    """
    if q:
        return book_db.update({"q": q})
    return books
```
- FastAPI 附加的条件约束 Query, 可加入支持的条件约束，比如字符串的最大长度，最小长度，注意：下面这种写法可能不会生效，跟FastAPI版本，python版本有关，可以用typing的附加注解Annotated来实现
```python
@router2.get("/book2/", name="参数的条件约束Query")
async def read_book2(q: Union[str, None] = Query(max_length=5, min_length=1)):
    """
    - param q: 使用FastAPI.Query 设置默认值，约束条件，[最大长度5, 最小长度1, 在部分FastAPI版本中不生效]
    """
    if q:
        book_db.update({"q": q})
        return book_db
    return books
``` 
- typing附加注解Annotated来实现的字符串参数的长度限制，其中Union是联合类型，表示q可是str 或者 None类型，Query与上文的用法一致，结尾的=None表示默认可以为空
```python
@router2.get("book2_1", name="Annotated注解中的条件约束")
async def read_book2_1(q: Annotated[Union[str, None], Query(max_length=5, min_length=1)] = None):
    if q:
        book_db.update({"q": q})
        return book_db
    return books
```
- Query约束中使用正则pattern，使用^限制字符串开头，$限制字符串结尾
```python
@router2.get("/book3/", name="参数Query约束中使用正则pattern")
async def read_book3(author: Union[str, None] = Query(default=None, pattern="^ls$"),):
    """
    - param author: Query使用pattern关键字约束 author的开头和结尾，限制为ls
    """
    if author:
        return books.get(author)
    return books
```
- 查询参数支持列表, Union联合类型中支持List[str]的写法，来接收列表， 也可以使用Union[list]写法
```python
@router2.get("book4", name="查询参数支持列表")
async def read_book4(author: Union[List[str], None] = Query(default=None)):
    """
    - param author: 查询参数支持一组列表数据，使用Union[List[str], None] 或者 Union[list, None]
    """
    if author:
        return author
    return books
```
- 使用 typing.Optional约束，Optional[str] 和 Union[str, None]是等价的，Optional[list]也可以指定参数是列表类型
```python
@router2.get("book4_1", name="使用list参数")
async def read_book4_1(author: Optional[list]):
    """
    - param author: 使用list 也可以表示入参为列表类型
    """
    if author:
        return author
    return books
```
- Query支持的元数据
>alias 别名 , title 标题, description 描述, deprecated 已废弃的接口
```python
@router2.get("/book5", name="Query的元数据")
async def read_book5(q: Optional[str] = Query(title='标题', alias="author", description="Query元数据的使用", deprecated=True)):
    if q:
        return books.get(q)
    return books

```
### 5、查询参数模型，使用Pedantic将一组相关的参数封装在一起，一次性声明和验证
- Pydantic.BaseModel 基础模型类，声明的模型需要继承它， Pydantic.Field 模型参数校约束方法
- typing.Literal 表示从列表中选择， 可指定默认选中值
- model_config = {"extra": "forbid"} 表示禁止额外参数
```python
class FilterParams(BaseModel):
    limit: int = Field(100, gt=0, le=100)
    offset: int = Field(0, gt=0)
    order_by: Literal["created_at", "updated_at"] = "created_at" # 检查特殊类型注解
    tags: list[str] = []
    model_config = {"extra": "forbid"} # 禁止额外的参数
```
- 使用Annotated附加额外元数据，用Query()标记这是一组查询参数, 他们将以?limit=100&offset=0&order_by=created_at的形式拼接在url后面
```python
@router.get('/items')
async def read_items(filter_query: Annotated[FilterParams, Query()] ):
    """
    :param filter_query: 特殊类型注解 Annotated [T, x]
    :return:
    """
    return filter_query
```
- model_config = {"extra": "forbid"} 禁止拼接额外的数据，如果在URL后面拼接未被定义的字段，会提示非法请求 

### 6、路径参数与数值校验
- Path约束与Query类似，主要是对数值型数据做验证，需要注意的是，路径参数是必须的且默认是字符串类型，即使使用Optional[int]声明了默认值None，可以是使用...来表示必填
- ge 大于等于， le小于等于
```python
from fastapi import Path

@router3.get("/{item_id}", name="Path的数值校验")
def read_item(item_id: Annotated[Optional[int], Path(..., ge=2, le=10)]) -> dict:
    """
    - param item_id: Path约束与Query类似，主要是对数值型数据做验证
    """
    if item_id:
        return {"item_id": item_id}
    return {"msg":"nothing!"}
```
- 浮点类型的数值校验, 查询参数使用Query约束，gt大于，lt小于
```python
@router3.get("/get_price/", name="浮点类型的数值校验")
async def get_price(price: float = Query(gt=0, lt=100.0)):
    if price:
        return {"price": price}
    return {"msg": "nothing!"}
```
- 参数的排序,路径参数默认值是None，python中有默认值的参数放在没有默认值的参数前，会报错;例如下面的代码,会跑出异常
```python
def paramOrder(item_id = 10, q:str):
    if item_id:
        print(q)
    else:
        print(q)

if __name__ == "__main__":
    paramOrder(9, "23")

##     def paramOrder(item_id = 10, q:str):                                     ^
## SyntaxError: non-default argument follows default argument
```
- 但是对fastapi 来说不关心顺序， 即使带有默认值的参数放在前面也不会报错，它会值自动检查参数类型
```python
@router3.get("/item1/{item_id}", name="路径参数与查询参数的排序")
def read_item(item_id: str, q:str):
    if q:
        return {"item_id": item_id}
    return {"msg":"nothing!"}
```
- 路径参数Path约束的元数据,和Query一样，支持title，description, alias
- 注意：这里有个坑，当路径参数名{item_id}, 与alias="itemId"定义的别名不一致时，会出现入参找不到的异常，如下面的报错
```python
	
Error: Unprocessable Content

Response body
Download
{
  "detail": [
    {
      "type": "missing",
      "loc": [
        "path",
        "itemId"
      ],
      "msg": "Field required",
      "input": null
    }
  ]
}
```
- 所以最好不使用别名，或者别名定义和路径参数名一致，如下
```python
@router3.get("/item2/{item_id}", name="Path约束的元数据")
def read_item(item_id: int = Path(title="标题", description="Path约束的元数据", deprecated=True)):
    if item_id:
        return {"item_id": item_id}
    return {"msg":"nothing!"}
```
- FastAPI关键字方式使用入参，* 以后表示使用关键字形式入参
```python
@router3.post("/create_item", name="python中位置参数、关键字参数的使用,*以后的表示关键字参数")
async def create_item(item_id: int, *,  name: str):
    return {"item_id": item_id, "name": name}
```
### 7、拓展
- typing中Union、Optional、Annotated的区别
- >Union[str, int] 联合类型，表示可以是str或者int类型
- >Optional[str] 语法糖，表示可是str类型或者None 等价于 Union[str, None]
- >Annotated 给类型附加额外的元数据(metadata)，不会影响类型本身，常见的用法 Annotated[Union[str, None], Query(default=None)]
- python中入参的顺序、位置参数、关键字参数的用法，口诀：/ * 分两头，arg收位置，kwargs收键值
- > / 左边的参数只能用位置传参
- > 在 / 和 * 之间的参数，即能位置传参，也能关键字传参
- > 在 * 以后的只能用关键字传参， 如 a=10
- > *args 捕获多余的位置参数，并形成元组 
- > **kwargs 捕获多余的关键字参数，形成字典
```python
def union_param(a, /, b, c=10 ,  *args, d, e=20, **kwargs):
    print(a, b, c, args, d, e, kwargs)

if __name__ == "__main__":
    # paramOrder(9, "23")
    union_param(1,2,3,4,5,6, d=15, e=25, extract1=33, extract2=34)
```
- > 输出结果：1 2 3 (4, 5, 6) 15 25 {'extract1': 33, 'extract2': 34}
- > 注意：默认值参数c没有使用关键字传参数也是可以的，而且只能使用位置传参数，因为python中有默认值的参数只能放在无默认值的参数之后，不能写成union_param(1,2,c=3,4,5,6...）
  > 位置参数d位于 / * 之间，他虽然是位置参数，但是也可以用关键字传参数，比如args后面的d可以这样传参union_param(1,2,c=3,4,5,6,d=15）,如果d和e都使用位置传参，会被收入arg中，输出元组

---

## 三、请求体
### 1、多个参数，混合使用 Path、Query、Body参数
- 可以混合使用 路径参数、查询参数 和请求体，FastApi知道如何处理
- 你可以在一个接口中，使用多个请求体参数
```python
from fastapi import APIRouter, Path, Query, Body
from pydantic import BaseModel, Field, HttpUrl
from typing import Annotated, Union

router = APIRouter()

class Item(BaseModel):
    name: str
    description: str | None = Field(default=None, title="The description of the item", alias="description", max_length=300)
    price: float = Field(gt=10, title="The price of the item", alias="price", le=100)
    tax: float | None = None

class User(BaseModel):
    name: str
    age: int | None = None

@router.put("/items1/{item_id}", name="混合使用路径参数、查询参数、请求体")
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
```
- 函数中单个参数默认是查询参数，但是可以用Body()标记为请求体的一部分
```python
@router.get("/items/{item_id}", name="将查询参数标记请求体")
async def get_item(item_id: Annotated[int, Path(title="The ID of the item to get")],
                   importance: Annotated[int, Body()],
                   item: Item | None = None,):
    result = {"item_id": item_id}
    result.update({"importance": importance})
    if item:
        result.update({"item": item})
    return result
```
- 使用参数名作为单个请求体的键名，Body(embed=True)
```python
@router.post("/items_1", name="使用参数名作为单个请求体的键名")
async def create_item(item: Item=Body(embed=True)):
    return item
```
> 在swagger上看到的请求入参则如下：\
{\
 "item": {\
    "name": "cc",\
    "description": "单个请求体的键名",\
    "price": 11,\
    "tax": 0\
  }\
}
- Body拥有和Path、Query相同的校验和元数据
```python
@router.post("/items_2", name="Body约束的元数据")
async def create_item(
        importance: Annotated[int, Body(title="title", ge=0, le=100, alias="importance", description="The importance of the item")],
        item: Item=Body()):
    result = {}
    if importance:
        result.update({"item": item})
        result.update({"importance": importance})
    return result
```
> 在swagger文档schema中可以看到 importance的元信息
> Body_Body_______requestBody_items_2_postCollapse allobject
importanceCollapse allinteger[0, 100]
The importance of the item
### 2、字段 Field，与Query、Path、Body的约束类似，Field需要直接从Pydantic直接引入
- 如下面的Item模型中, description 和 price 都使用了Filed约束
```python
class Item(BaseModel):
    name: str
    description: str | None = Field(default=None, title="The description of the item", alias="description", max_length=300)
    price: float = Field(gt=10, title="The price of the item", alias="price", le=100)
    tax: float | None = None
```
> 当入参 price = 9 时，参数校验失败会给出提示
> {\
  "detail": [\
    {\
      "type": "greater_than",\
      "loc": [\
        "body",\
        "item",\
        "price"\
      ],\
      "msg": "Input should be greater than 10",\
      "input": 9,\
      "ctx": {\
        "gt": 10\
      }\
    }\
  ]\
}
### 3、嵌套模型
- 模型的字段设置为列表类型，指定列表中的数据类型 typing.List[str]
```python
class ItemModel(BaseModel):
    name: str
    description: str | None = None
    tags: List[str] = None
```
- 模型的字段设置为列表类型, 不指定列表中的数据类型
```python
class MarkModel(BaseModel):
    name: str
    tags: list = []
```
- 模型的字段设置为集合类型，并指定集合中元素的类型 typing.Set[str],如下
```python
class DistinctModel(BaseModel):
    name: str
    tags: Set[str] = set()
    
@router2.patch("/items/{item_id}", name="模型字段中嵌套Set类型，实现去重复")
async def update_item(item: DistinctModel):
    return item
```
>当输入的"tags": ["a","a","c","b","c"]会自动去重复\
> 结果如下 Response body\
{\
  "name": "mark",\
  "tags": [\
    "b",\
    "a",\
    "c"\
  ]\
}
- 模型的字段设置为原生集合类型,且不限制元素类型，可以对入参自动进行去重复，如
```python
class SetModel(BaseModel):
    name: str
    tags: set = set()
    
@router2.post("/tags", name="模型的字段设置为原生集合类型，实现去重复")
async def create_item(item: SetModel):
    return item
```
> 当输入的有重复的字符串和数值时，会自动根据类型去重\
> 输入 {\
  "name": "string",\
  "tags": ["a","b","a","1",1,2,3,2,3]\
}\
> 输出 {\
  "name": "string",\
  "tags": [
    1,
    2,
    3,
    "1",
    "b",
    "a"
  ]\
}
- 模型的字段除了常用的(str,int,float)类型，还可以定义为复杂的类型，如Pydantic 的 HttpUrl
```python
class Pkg(BaseModel):
    url: HttpUrl  # 引入pydantic 额外的类型
    description: str | None = None

@router2.put("/pkgs/{pkg_id}", name="模型字段定义为Pydantic的HttpUrl")
def update_package(pkg_id: int ,package: Pkg) -> dict[str, int | Pkg]:
    return {"pkg_id":pkg_id, "package": package}
```
> 当输入的不是标准URL类型时会给出错误提示\
>    "msg": "Input should be a valid URL, relative URL without a base",\
      "input": "123",\
      "ctx": {\
        "error": "relative URL without a base"\
      }
- 模型的字段设置为一个模型，实现模型嵌套
```python
class Pkg(BaseModel):
    url: HttpUrl  # 引入pydantic 额外的类型
    description: str | None = "url 字段设置Pedantic.HttpUrl，实现输入校验"

class NestingModel(BaseModel):
    name: str | None = "parent字段嵌套Pkg模型"
    description: str | None = None
    parent: Pkg = None
```
- 模型的字段设置为一个模型列表
```python
class SubPkg(BaseModel):
    name: str
    description: Union[str, None] = "parent字段嵌套的Pkg类型是一个模型列表"
    parent: List[Pkg] | None = None  #嵌套模型
```
> 在swagger提示中可看到parent支持多个pkg模型\
> {\
  "name": "string",\
  "description": "parent字段嵌套的Pkg类型是一个模型列表",\
  "parent": [\
    {\
      "url": "https://example.com/",\
      "description": "url 字段设置Pedantic.HttpUrl，实现输入校验"\
    }\
  ]\
}
- 模型的深度嵌套，支持模型多层嵌套 pkgs字段嵌套了 SubPkg, SubPkg.parent嵌套了List[Pkg]
```python
class DeepNesting(BaseModel):
    name: str
    description: str | None = "模型可以任意深度的嵌套"
    pkgs: SubPkg | None = None 
```
- 纯模型列表的请求体, 可以直接使用List[module]来定义
```python
@router2.post("/nestingList",name="模型定义为纯列表类型的请求体")
async def create_item(item: List[Pkg]):
    return item
```
> 在swagger上可以看到，模型是一个列表输入
> Example Value\
Schema\
[\
  {\
    "url": "https://example.com/",\
    "description": "url 字段设置Pedantic.HttpUrl，实现输入校验"\
  }\
]
- 任意 dict 构成的请求体, 在python中dict中，key必须是字符串类型的，但是在FastApi中，key可以是任意单一类型的，如int, float, 他会自动将数值类型的字符串识别成int或者float类型，如"1"将被识别成int
```python
@router2.post("/dictBody", name="构建任意dict请求体")
async def create_item(item: dict[int, float], tags: dict[float,str]):
    result = {"item": item, "tags": tags}
    return result
```
- 当入参item 的key不是数值型字符串，会检验错误
> {\
  "item": {\
    "a": 0\
  },\
  "tags": {\
    "3.14": "圆周率"\
  }\
}\
> "msg": "Input should be a valid integer, unable to parse string as an integer", "input": "a"
- 当入参tags 的vale不是字符串，也会检验错误
> {\
  "item": {\
    "3": 0\
  },\
  "tags": {\
    "3.14": 2\
  }\
}
> "msg": "Input should be a valid string","input": 2
### 4、请求体拓展，示例与额外的数据类型
- 在模型添加model_config 实现，会直接添加在请求体中
```python
class Schema(BaseModel):
    """
    额外的请求体参数, 指定示例schema
    """
    name: str = Field(examples=['Field 提供的参数说明'])
    description: str | None = Field(examples=['Field 提供的参数说明'])
    price: int | None = None
    model_config = {  # schema 可以直接填充在请求体中
        "json_schema_extra": {
            "example": {
                "name": "polly",
                "description": "请求体额外的信息-示例",
                "price": 109 
            }
        }
    }
```
- 字段Field中也可以添加示例examples
```python
class FieldSchema(BaseModel):
    name: str = Field(examples=['Field 提供的参数说明'])
    description: str | None = Field(examples=['Field 提供的参数说明'])
    price: int | None = None
```
- 请求体Body中也可添加示例examples
```python
@router3.put("/BodySchema/{sch_id}", name="给请求体添加额外示例")
async def update_schema(
        sch_id: int,
        schema: Annotated[
            Schema,
            Body(examples=[
                {"name": "tiky",
                 "description": "给请求体中添加示例", }
                ]
            )
        ]
) -> dict[str, int | Schema]:
```
- 请求体额外的数据类型
> - uuid: "通用唯一标识符" ，在许多数据库和系统中用作ID, 是str类型
> - datetime.date 在请求和响应中将表示为 ISO 8601 格式的 str ，比如: 2008-09-15.
> - datetime.datetime 在请求和响应中将表示为 ISO 8601 格式的 str ，比如: 2008-09-15T15:53:00+05:00.
> - datetime.timedelta, 在请求和响应中将表示为 float 代表总秒数
> - frozenset 在请求和响应中，作为 set 对待,请求中消除重复，响应中转化成list
> - bytes 标准的 Python bytes 在请求和响应中被当作 str 处理
> - Decimal 标准的 Python Decimal 在请求和响应中被当做 float 一样处理
```python
class ExtractDataModel(BaseModel):
    name: str
    description: str | None = None
    price: Decimal
    tags: frozenset[int] | None = None

@router3.post("/extractDataType/{{id}}", name="decimal类型")
async def create_schema(id: int,
                        item: Annotated[ExtractDataModel,
                            Body( examples=[{
                                "name": "decimal",
                                "description":"额外的数据类型",
                                "price": Decimal("109"),
                                "tags": [1,2,2,3]
                                }]
                            )
                        ]):
    result = {"id": id, "item": item}
    return result
```
> 可以看到输入的数据成功处理\
> 输入\
> {
  "name": "decimal",
  "description": "额外的数据类型",
  "price": "109",
  "tags": [
    1,
    2,
    2,
    3
  ]
}\
> 响应\
> {
  "id": 12,\
  "item": {\
    "name": "decimal",\
    "description": "额外的数据类型",\
    "price": "109",\
    "tags": [\
      1,\
      2,\
      3\
    ]\
  }\
}
### 5、表单数据与模型
- 表单数据
- 表单模型
### 6、文件与表单
- 文件上传
- 文件与表单同时存在