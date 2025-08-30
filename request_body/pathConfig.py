from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel, EmailStr
from datetime import datetime
router5 = APIRouter(
    prefix="/pathConfig",
    tags=["路径操作配置"]
)

class Item(BaseModel):
    name: str
    age: int
    email: EmailStr | None = None
    tags: list[str] | None = None
    create_at: datetime | None = None


NameDB = {
    "Lily":{"name":"Lily", "age":35, "email":"Lily366@163.com"},
    "Piter":{"name":"Piter", "age":32, "tags":["bright", "happy"]},
    "Join":{"name":"Join", "age":40, "create_at":datetime.now()},
}

@router5.get("/item/{item_id}", status_code=status.HTTP_200_OK, summary="状态码")
async def get_item(item_id: str):
    if item_id in NameDB:
        return NameDB[item_id]
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="item not found")

@router5.get("/items/", name="描述和响应描述", description="示例描述信息", response_description="响应描述示例")
async def get_items():
    return NameDB

@router5.get("/detail/{name}", summary="tags和弃用标记", tags=["路径操作配置-弃用标记"], deprecated=True)
async def get_detail(name: str):
    if name in NameDB:
        return NameDB[name]
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="item not found")