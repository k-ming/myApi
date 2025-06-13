#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 15 19:57:49 2025
@author: hb32366
"""

from fastapi import FastAPI, Depends
from .dependencies import get_query_token, get_token_header
from enum import Enum
from .src import user, searchModle, requestBody, requestExtra, requestFormData
from .routers import items,formFile
from .internal import admin
import os
import sys
from starlette.staticfiles import StaticFiles
from .depends import pyDepends, pyDependYield
from fastapi.security import OAuth2PasswordBearer
from .auth2 import oauth_token

app = FastAPI(dependencies=[])
static_path = os.path.join(os.path.dirname(__file__), "static") # 使用os.path.join获取
# print(static_path)
app.mount("/static", StaticFiles(directory=static_path), name="static") # 挂载静态文件
# 修改doc使用的静态文件
sys.modules["fastapi.openapi.docs"].get_swagger_ui_html.__kwdefaults__["swagger_js_url"] = "/static/swagger-ui-bundle.js"
sys.modules["fastapi.openapi.docs"].get_swagger_ui_html.__kwdefaults__["swagger_css_url"] = "/static/swagger-ui.css"

app.include_router(user.router)
app.include_router(items.router)
app.include_router(searchModle.router, prefix='/searchAdd')
app.include_router(requestBody.router, prefix='/requestBody', tags=['requestBody'])
app.include_router(admin.router,
                   prefix='/admin',
                   dependencies=[Depends(get_token_header)],
                   responses={418: {"description": "I'm a teapot"}}, tags=['admin'])
app.include_router(requestExtra.router, prefix='/requestExtra', tags=['requestExtra'])
app.include_router(formFile.router, prefix="/formFile", tags=['Form'])
app.include_router(requestFormData.router, prefix='/requestFormData', tags=['Form'])
app.include_router(pyDepends.router)
app.include_router(pyDependYield.router)
app.include_router(oauth_token.router)



@app.get("/", tags=['root'])
async def root():
    return {"msg": "hello fastapi"}


# 路径参数--并指定参数类型
@app.get("/{item_id}", tags=['root'])
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
