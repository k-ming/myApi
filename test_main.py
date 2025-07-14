from fastapi.testclient import TestClient
from .main import app

client = TestClient(app)
'''
使用httpx 配合 pytest 做单元测试
执行pytest命令时，需要再项目的上层目录，如
 pwd
/Users/hb32366/devs
则执行 pytest myApi/
会执行 myApi项目下所有的单元测试module
'''

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "hello fastapi"}

def test_module():
    response = client.get("/models/alexnet")
    assert response.status_code == 200
    assert response.json() == {"model_name": "alexnet", "msg": "Deep Learning FTW!"}