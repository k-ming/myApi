from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    """
    定义基础数据模型，后面的创建、更新、查询表模型继承于此
    """
    name: str = Field(index=True)
    age: int | None = Field(default=None, index=True)


class User(UserBase, table=True):
    """
    定义User表模型， 继承自UserBase, （不含table=True的都是数据模型）
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
    type: str | None = Field(default='user')
    model_config = {
        'json_schema_extra': {
            'example': {
                'name': 'user',
                'age': 18,
                'secret_name': 'user',
                'type': 'manage'
            }
        }
    }


class UserUpdate(UserBase):
    """
    定义UserUpdate数据模型，用于更新数据，虽然它继承自UserBase，但是它所有字段都重新定义，且可选
    """
    name: str | None = None
    age: int | None = None
    secret_name: str | None = None