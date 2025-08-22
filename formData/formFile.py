from typing import List, Annotated
from pydantic import BaseModel

from fastapi import APIRouter, File, UploadFile, Form

router1 = APIRouter(
    prefix="/file",
    tags=["文件"]
)

class FormModel(BaseModel):
    name : str
    token: str | None = None


@router1.post("/files", name="file文件和表单数据")
def create_file(file: bytes | None = File(description="a file read as byte", default=None), token: str = Form()):
    return {"len_file": len(file), "token": token}

@router1.post("/uploadFiles", name="uploadFile上传大文件")
def create_uploadFile(file: UploadFile | None= File(description="a file read as byte")):
    return {"file": file.filename}

@router1.post("/moreFiles", name="批量上传文件")
def create_moreFile(files: List[UploadFile]):
    return {"files": files}

