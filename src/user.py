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

router = APIRouter()

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    age: int | None = Field(default=None, index=True)

sql_url = "mysql+pymysql://{}:{}@{}/{}?charset=utf8mb4".format('root','root', 'mysql:3306','myApi')
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

@router.post("/user/", tags=["users"])
def create_user(user: User, session: SessionDep) -> User:
    """
    Create a new user， 如果user.id == 0 ,需要将其设置为None，否则refresh会报错
    :param user: 用户model
    :param session: 获取数据库回话
    :return: 用户model
    """
    if user.id is not None:
        user.id = None
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.get("/users/", tags=["users"])
async def read_users():
    return [{"username": "Rick"}, {"username": "Morty"}]


@router.get("/users/me", tags=["users"])
async def read_user_me():
    return {"username": "fakecurrentuser"}


@router.get("/users/{username}", tags=["users"])
async def read_user(username: str):
    return {"username": username}