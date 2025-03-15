#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 01:37:22 2025

@author: hb32366
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pygments.lexer import default
from sqlmodel import Field, SQLModel, create_engine, select, Session
from typing import Annotated
import json

router = APIRouter()


class UserBase(SQLModel):
    """
    定义基础数据模型（不含table=True的都是数据模型），后面的创建、更新、查询表模型继承于此
    """
    name: str = Field(index=True)
    age: int | None = Field(default=None, index=True)


class User(UserBase, table=True):
    """
    定义User表模型， 继承自UserBase
    """
    id: int | None = Field(default=None, primary_key=True)
    secret_name: str


class UserPub(UserBase):
    """
    定义UserPub数据模型，继承自UserBase, 用于返回给客户端，但是它不包含 secret_name，且重新声明了id，id是必须的
    """
    id: int


class UserCreate(UserBase):
    """
    定义UserCreate数据模型，继承自UserBase， 它继承了 name, age字段，且声明了必选字段secret_name， 用于验证客户数据的模型
    """
    secret_name: str


class UserUpdate(UserBase):
    """
    定义UserUpdate数据模型，用于更新数据，虽然它继承自UserBase，但是它所有字段都重新定义，且可选
    """
    name: str | None = None
    age: int | None = None
    secret_name: str | None = None


sql_url = "mysql+pymysql://{}:{}@{}/{}?charset=utf8mb4".format('root', 'root', '148.100.112.145:3306', 'myApi')
# 注意推上GitHub时host要修改成功mysql容器名称mysql， 因为时容器间通信，dev本地调试时改成148.100.112.145:3306
engine = create_engine(sql_url, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


@router.on_event("startup")
def on_startup():
    create_db_and_tables()


@router.post("/user/", tags=["users"], response_model=UserPub)
def create_user(user: UserCreate, session: SessionDep) -> User:
    """
    response_model=UserPub 用于返回给客户端数据模型，会隐藏secret_name字段
    user: UserCreate 创建数据模型，拥有name,age,secret_name字段
    :param user: 用户model
    :param session: 获取数据库回话
    :return: 用户model
    """
    db_user = User.model_validate(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.get("/users/", tags=["users"], response_model=list[UserPub])
async def read_users(session: SessionDep, offset=0, limit: Annotated[int, Query(le=100)] = 100, ) -> list[UserPub]:
    """
    response_model=list[UserPub] 返回值隐藏了secret_name
    :param session:
    :param offset:
    :param limit:
    :return:
    """
    user_list = session.exec(select(User).offset(offset).limit(limit)).all()
    return user_list


@router.get("/users/{user_id}", tags=["users"], response_model=UserPub)
async def read_user(user_id: int, session: SessionDep) -> UserPub:
    """
    查询单个用户
    :param user_id:
    :param session:
    :return:
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/users/{user_id}", tags=["users"], response_model=UserPub)
def update_user(user_id: int, user: UserUpdate, session: SessionDep) -> UserPub:
    """
    更新单个用户
    :param user_id:
    :param user:
    :param session:
    :return:
    """
    user_db = session.get(User, user_id)
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")
    user_data = user.model_dump(exclude_unset=True)
    user_db.sqlmodel_update(user_data)
    session.add(user_db)
    session.commit()
    session.refresh(user_db)
    return user_db

@router.delete("/users/{user_id}", tags=["users"])
def delete_user(user_id: int, session: SessionDep) :
    """
    删除单个用户, 无响应model
    :param user_id:
    :param session:
    :return:
    """
    user_db = session.get(User, user_id)
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user_db)
    session.commit()
    return {"ok": True}