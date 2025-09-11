from sqlmodel import create_engine, SQLModel, Session
from typing import Annotated
from fastapi import Depends

# 设置数据库连接host
dev_host = 'ec2-78-12-183-10.mx-central-1.compute.amazonaws.com'
test_host = 'mysql'

# 设置数据库engine的URL
sql_url = "mysql+pymysql://{}:{}@{}/{}?charset=utf8mb4".format('test', '123456', '%s:3306' % dev_host, 'myApi')
# 注意推上GitHub时host要修改成功mysql容器名称mysql， 因为时容器间通信，dev本地调试时改成148.100.112.145:3306
engine = create_engine(sql_url, echo=True, pool_size=20, max_overflow=10, pool_recycle=3600) # 设置链接池大小，最大溢出数，回收时长

# 创建数据库和数据表
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# 获取数据会话
def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]