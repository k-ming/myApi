from datetime import datetime
from typing import final

from fastapi import APIRouter
from pydantic import BaseModel, EmailStr
from fastapi.encoders import jsonable_encoder

'''
- 把输入数据转换为以 JSON 格式存储的数据
- 使用put更新数据，用于替换现有数据
- 使用path 或者 put 更新部分数据
'''
router4 = APIRouter(
    prefix="/updateData",
    tags=["请求体-更新数据"]
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

@router4.put("/fullUpdate/", name="全量更新，输入数据转换为JSON 格式存储")
async def updateData(item_id: str, item: Item):
    if item_id in NameDB:
        item_encode = jsonable_encoder(item) # 此处会把 create_at转换成字符串
        NameDB[item_id]= item_encode
        return NameDB[item_id]
    else:
        return {"msg": "no such item !", "code": 404}

@router4.patch("/patchUpdate/", name="使用patch部分更新数据")
async def patchUpdate(item_id: str, item: Item ):
    if item_id in NameDB:
        update_data = NameDB[item_id]
        update_model = Item(**update_data) # 使用存在的数据生成一个模型
        print("update_model:", update_model)
        update_unset = item.model_dump(exclude_unset=True) # 把入参模型设置为不包含默认值
        final_data = update_model.model_copy(update=update_unset)  # 使用pedantic的model_copy拷贝模型，并设置更新数据
        print("final_data:", final_data)
        NameDB[item_id]= jsonable_encoder(final_data) # 更新数据
        return NameDB[item_id]
    else:
        return {"msg": "no such item !", "code": 404}


@router4.put("/putPartlyUpdate/", name="使用put实现部分数据更新")
async def putPartlyUpdate(item_id: str, item: Item):
    if item_id in NameDB:
        update_data = NameDB[item_id]
        update_model = Item(**update_data) # 使用查询到已有的数据生成一个model
        update_unset = item.model_dump(exclude_unset=True)  # 入参模型设置为不包含默认值
        final_data = update_model.model_copy(update=update_unset) # 使用model_copy(update=update_unset) 组合数据
        NameDB[item_id]= jsonable_encoder(final_data)
        return NameDB[item_id]

