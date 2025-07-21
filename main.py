"""
Main file to start.
"""

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.router import main_router
# from app.robot import robot

# Initialize FastAPI
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(main_router)


if __name__ == "__main__":
    try:
        uvicorn.run(app, host="0.0.0.0", port=8030)
    finally:
        # robot.cleanup()
        pass



# app = Flask(__name__)
# @app.route("/")
# def main_page():
#     print("Page is working")
#     return render_template("service/templates/index.html")

# @app.route('/video_feed')
# def video_feed():
#     return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# @app.route('/status')
# def status():
#     global imgname
#     return send_file('static/{}'.format(imgname), mimetype='image/gif')

# @app.route('/process', methods=["GET", "POST"])
# def background_process_test():
#     if request.method == "POST":
#         data = request.get_json()
#         if data == "S" :
#             print("the robot stops")
#             stop()
#         elif data == "C" :
#             print("NN processing -- ON/OFF")
#             turn_NN_on()

#     return ("nothing")

# if __name__ == "__main__":
#     app.run(debug=True, host = ip_adr, port=8030, threaded = True)

