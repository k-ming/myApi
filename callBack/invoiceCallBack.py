from typing import Union

import httpx
from fastapi import APIRouter
from pydantic import HttpUrl, BaseModel

router = APIRouter()


class Invoice(BaseModel):
    id: str
    title: Union[str, None] = None
    customer: str
    total: float


class InvoiceEvent(BaseModel):
    description: str
    paid: bool


class InvoiceEventReceived(BaseModel):
    ok: bool


invoice_callBack = APIRouter()

@router.post("/get/{invoice_id}", response_model=InvoiceEventReceived)
def receive_invoice_event(invoice_id: str, body: InvoiceEvent):
    """
    用于模拟客户端接收回调
    :param invoice_id:
    :param body:
    :return:
    """
    return {"ok": True}

@invoice_callBack.post("{$callback_url}/Invoice/get/{$request.body.id}", response_model=InvoiceEventReceived)
def invoice_notification(body: InvoiceEvent):
    """
    回调接口文档定义，实际不会调用
    :param body:
    :return:
    """
    pass


@router.post("/invoices", callbacks=invoice_callBack.routes)
async def create_invoice(invoice: Invoice, callback_url: Union[HttpUrl, None] = None):
    """
    创建发票，并实现回调
    :param invoice:
    :param callback_url:
    :return:
    """
    print(f"[主接口]收到发票请求 {invoice}]")
    event_data = {
        "description": f"Payment for {invoice.id} successfully",
        "paid": True
    }
    # 如果调用方提供了回调地址，则发送真正的 http 回调
    if callback_url:
        callback_full_url = f"{callback_url}Invoice/get/{invoice.id}"
        print(f"[主接口]正在回调{callback_full_url}")
        async with httpx.AsyncClient() as client:
            r = await client.post(callback_full_url, json=event_data)
        print(f"[主接口]回调响应:{r.status_code}{r.text}")
        return {
            "msg": "Invoice processed and callback sent",
            "callback_status": r.status_code,
            "callback_response": r.json()
        }
    return {"message": "Invoice created"}


invoice_send_response = APIRouter()


@invoice_send_response.post("/getInvoice", response_model=InvoiceEventReceived)
def get_invoice(body: InvoiceEvent):
    return {"ok": True}
