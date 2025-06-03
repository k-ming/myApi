from fastapi import APIRouter, File, UploadFile, Form

router = APIRouter()

@router.post("/files")
def create_file(file: bytes | None = File(description="a file read as byte", default=None), token: str = Form()):
    return {"len_file": len(file), "token": token}

@router.post("/uploadFiles")
def create_uploadFile(file: UploadFile | None= File(description="a file read as byte"), token: str = Form()):
    return {"file": file.filename, "token": token}