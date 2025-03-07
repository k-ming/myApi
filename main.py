#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 15 19:57:49 2025
@author: hb32366
"""

from fastapi import FastAPI
import pydantic
from enum import Enum
from src import user
import os
import sys

# 处理ubuntu系统中，找不到model的问题
current_dir = os.path.dirname(__file__)
file_path = os.path.join(current_dir, 'src', 'user.py')
sys.path.append(file_path)

app = FastAPI()

app.include_router(user.router)

@app.get("/")
async def root():
    return {"msg":"hello fastapi"}

# 路径参数--并指定参数类型
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {'item_id':item_id}


# 枚举
class ModelName(str, Enum):
    alexnet = 'alexnet'
    resnet = 'resnet'
    lenet = 'lenet'

@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, 'msg': "Deep Learning FTW!"}
    elif model_name is ModelName.resnet:
        return {"model_name": model_name, "msg": "LeCNN all the images"}
    
    return {"model_name": model_name, "msg":"Have some residuals"}