#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 15 19:57:49 2025
@author: hb32366
"""

from fastapi import FastAPI, Depends, Request
from starlette.staticfiles import StaticFiles
from .depends import pyDepends, pyDependYield
from .dependencies import get_token_header
from enum import Enum
import sys, time

import request_body, parameters, formData, responseModel
from .auth2 import oauth_token,user, admin
from callBack import invoiceCallBack
from .subapp import subapi  # 引入子应用

app = FastAPI(dependencies=[])

# fastapi 挂载静态文件目录
app.mount("/static", StaticFiles(directory="myApi/static"), name="static") # 挂载静态文件
# 修改doc使用的静态文件
sys.modules["fastapi.openapi.docs"].get_swagger_ui_html.__kwdefaults__["swagger_js_url"] = "/static/swagger-ui-bundle.js"
sys.modules["fastapi.openapi.docs"].get_swagger_ui_html.__kwdefaults__["swagger_css_url"] = "/static/swagger-ui.css"

# 挂载子应用
app.mount("/subapp", subapi)

app.include_router(user.router)
app.include_router(parameters.router) # 三种参数：路径参数、查询参数、请求体
app.include_router(parameters.router2) # 查询参数和字符串校验
app.include_router(parameters.router3) # 路径参数和字符串校验
app.include_router(parameters.router4) # 查询参数模型化
app.include_router(request_body.router1) # 请求体-多个参数
app.include_router(request_body.router2) # 请求体-字段
app.include_router(request_body.router3) # 请求体-额外的信息，示例和数据类型
app.include_router(formData.router1) #表单数据
app.include_router(formData.router2) # 文件上传
app.include_router(responseModel.router1) # 响应模型
app.include_router(responseModel.router2) # 多个模型和模型的继承
app.include_router(admin.router,
                   prefix='/admin',
                   dependencies=[Depends(get_token_header)],
                   responses={418: {"description": "I'm a teapot"}}, tags=['admin'])

app.include_router(pyDepends.router)
app.include_router(pyDependYield.router)
app.include_router(oauth_token.router)
app.include_router(invoiceCallBack.router, prefix='/Invoice', tags=['开发票回调'])



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


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
