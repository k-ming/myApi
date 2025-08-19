# fastapi 学习
## 一、 启动方式
### 1、使用 unicorn 启动
```
# 需要从项目最外层启动，否则会报错 ImportError: attempted relative import with no known parent package 可参考：https://stackoverflow.com/questions/76939674/fastapi-attempted-relative-import-beyond-top-level-package
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
- FastAPI 附加的条件约束 Query, 可加入支持的条件约束，比如字符串的最大长度，最小长度，注意：下面这种写法可能不会生效，跟FastAPI版本，python版本有关，可以用type的附加注解Annotated来实现
```python
@router2.get("/book2/", name="参数的条件约束Query")
async def read_book2(q: Union[str, None] = Query(Max_length=5, Min_length=1)):
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

### 5、路径参数与数值校验
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
### 6、拓展
- typing中Union、Optional、Annotated的区别
- >Union[str, int] 联合类型，表示可以是str或者int类型
- >Optional[str] 语法糖，表示可是str类型或者None 等价于 Union[str, None]
- >Annotated 给类型附加额外的元数据(metadata)，不会影响类型本身，常见的用法 Annotated[Union[str, None], Query(default=None)]
- python中入参的顺序、位置参数、关键字参数的用法，口诀：/ * 分两头，arg收位置，kwargs收键值
- > / 左边的参数只能用位置传参
- > 在 / 和 * 之间的参数，即能位置传参，也能关键字传参
- > 在 * 以后的智能用关键字传参， 如 a=10
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
- > 注意：默认值参数c没有使用关键字传参数也是可以的，而且只能使用关键字传参数，因为python有默认值的参数只能放在无默认值的参数之后
  > 位置参数d位于 / * 之间，他虽然是位置参数，但是也可以用关键字传参数