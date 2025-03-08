from fastapi import APIRouter


router = APIRouter()

@router.post("/")
async def update_item(item_id:str):
    return {"item_id": item_id}