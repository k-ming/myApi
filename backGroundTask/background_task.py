from fastapi import APIRouter,BackgroundTasks

router = APIRouter(
    prefix="/backgroundTasks",
    tags=["后台任务"]
)

def write_notification(email: str, message=''):
    with open('./log.txt', mode='w') as email_file:
        content = f'notification for {email}: {message}'
        email_file.write(content)


@router.post("/send-notification/{email}")
async def send_notification(email:str, background_tasks: BackgroundTasks):
    background_tasks.add_task(write_notification, email=email, message="some notification")
    return {"message": "Notification sent in the background"}