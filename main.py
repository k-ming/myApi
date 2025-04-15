#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 15 19:57:49 2025
@author: hb32366
"""

from fastapi import FastAPI, Depends
from .dependencies import get_query_token, get_token_header
from enum import Enum
from .src import user, searchModle, requestBody, requestExtra
from .routers import items,files
from .internal import admin
import os
import sys


app = FastAPI(dependencies=[Depends(get_query_token)])

app.include_router(user.router)
app.include_router(items.router)
app.include_router(searchModle.router, prefix='/searchAdd')
app.include_router(requestBody.router, prefix='/requestBody', tags=['requestBody'])
app.include_router(admin.router,
                   prefix='/admin',
                   # dependencies=[Depends(get_token_header)],
                   responses={418: {"description": "I'm a teapot"}}, tags=['admin'])
app.include_router(requestExtra.router, prefix='/requestExtra', tags=['requestExtra'])
app.include_router(files.router, prefix="/file", tags=['files'])



@app.get("/", tags=['root'])
async def root():
    return {"msg": "hello fastapi"}


# 路径参数--并指定参数类型
@app.get("/items/{item_id}", tags=['root'])
async def read_item(item_id: int):
    return {'item_id': item_id}


# 枚举
class ModelName(str, Enum):
    alexnet = 'alexnet'
    resnet = 'resnet'
    lenet = 'lenet'


@app.get("/models/{model_name}", tags=['root'])
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, 'msg': "Deep Learning FTW!"}
    elif model_name is ModelName.resnet:
        return {"model_name": model_name, "msg": "LeCNN all the images"}

    return {"model_name": model_name, "msg": "Have some residuals"}
