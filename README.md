# fastapi 学习
## 启动方式
需要从项目最外层启动，否则会报错 ImportError: attempted relative import with no known parent package 可参考：https://stackoverflow.com/questions/76939674/fastapi-attempted-relative-import-beyond-top-level-package
```
uvicorn myApi.main:app
```
