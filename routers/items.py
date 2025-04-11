import inspect

from fastapi import APIRouter, Depends,HTTPException
from ..dependencies import get_token_header
import os, sys

router = APIRouter(
    prefix="/items",
    tags=["items"],
    dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)

fake_items_db = {"plumbus": {"name": "Plumbus"}, "gun": {"name": "Portal Gun"}}

@router.get("/")
async def read_items():
    return fake_items_db

@router.get("/{item_id}")
async def read_item(item_id: str):
    if item_id not in fake_items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"name":fake_items_db[item_id]["name"], "item_id":item_id}

@router.put("/{item_id}",
            tags=["items_extra"],
            responses={403: {"description": "operation is forbidden"}})
async def update_item(item_id: str):
    """
    - 在items module中的子方法单独定义了 tags, 不会覆盖module的域 items，会单独生成 items_extra 域
    - **param**: item_id 必须为 plumbus
    """
    if item_id != "plumbus":
        raise HTTPException(status_code=403, detail="you can only update plumbus")
    return {"item_id":item_id, "name":"The great Plumbus"}
