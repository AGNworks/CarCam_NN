"""
Main router
"""

from fastapi import Request, APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, StreamingResponse

from app.camera import camera
from app.robot import robot


# Setup templates
templates = Jinja2Templates(directory="templates")

# Router for NN processes
main_router = APIRouter()


@main_router.get("/", response_class=HTMLResponse)
async def main_page(request: Request):
    """
    Show main page
    """

    print("Page is working")
    return templates.TemplateResponse("index.html", {"request": request})

@main_router.get('/video_feed')
async def video_feed():
    """
    Create video from (just camera)
    """

    return StreamingResponse(
        camera.generate_frames(),
        media_type='multipart/x-mixed-replace; boundary=frame'
    )


@main_router.get('/seg_feed')
async def seg_feed():
    """
    Create video from (just camera)
    """

    return StreamingResponse(
        camera.gen_nn_frames(),
        media_type='multipart/x-mixed-replace; boundary=frame'
    )

@main_router.post('/process')
async def get_command_from_user(request: Request):
    """
    User command processing.
    """

    data = await request.json()

    if data == "R":
        print("The robot starts move if NN is started")
        robot.forward()
        robot.smart_moving = True

    if data == "S":
        print("The robot stops")
        robot.smart_moving = False
        robot.stop()

    elif data == "C":
        robot.switch_nn()
        print(f"NN processing -- {robot.nn_on}")

    return {"status": "success"}
