from fastapi import Header, HTTPException

async def get_token_header(token: str = Header(...)):
    if token != "X-Token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")

async def get_query_token(token: str):
    if token != "Jessica":
        raise HTTPException(status_code=400, detail="No Jessica token provided")