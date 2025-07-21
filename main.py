"""
Main file to start.
"""

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.router import main_router
from app.robot import robot
from app.camera import camera

# Initialize FastAPI
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(main_router)


if __name__ == "__main__":
    try:
        uvicorn.run(app, host="0.0.0.0", port=8030)
    finally:
        robot.cleanup()
        camera.shutdown()
