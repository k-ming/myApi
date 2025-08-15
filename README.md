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

@router.post("/create_book", tags=["items"])
def create_book(id: str, item: Books):
    """
    - **fake_db** 只能接受与json兼容的数据
    - **jsonable_encoder** 可以将与json不兼容的时间格式数据转化成字符串格式
    """
    json_compatibler_item_data = jsonable_encoder(item)
    book_db[id] = json_compatibler_item_data
    return book_db
```
