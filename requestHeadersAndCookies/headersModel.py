from datetime import datetime
from typing import List
from fastapi import APIRouter, Header
from pydantic import BaseModel

router1 = APIRouter(
    prefix="/headers",
    tags=["header参数与模型"]
)

class HeadersModel(BaseModel):
    Agent: str | None = None
    X_Token: List[str] | None = None
    timestamp: str | None = datetime.timestamp(datetime.now())


@router1.get("/headerParam", name="header参数")
async def get_headers(token: str = Header(...)):
    return {"token": token}

@router1.put("/listHeaders", name="一组同名的header")
async def put_headers(token: List[str] = Header(...)):
    return {"token": token}

@router1.patch("/concatLine", name="Header自动把下划线转成连接线，不区分大小写")
async def patch_headers(X_Token: str=Header(...)):
    return {"X-Token": X_Token}

@router1.patch("/underLine", name="Header禁用下划线转连接符")
async def patch_headers(X_Token: str=Header(..., convert_underscores=False)):
    return {"X-Token": X_Token}

@router1.post("/headerModel", name="Header模型")
async def post_headers(headers: HeadersModel):
    return {"headers": headers}