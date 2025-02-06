from flask import Flask, Response
from camera_controller import CameraController


class MJpegStreamServer:
    def __init__(self, camera_controller: CameraController, port: int):
        # Initialize the MJPEG stream server with the camera controller and port
        self.camera = camera_controller
        self.port = port
        self.app = Flask(__name__)
        self.app.add_url_rule("/", view_func=self.stream)

    def stream(self):
        # Stream the MJPEG frames
        return Response(
            self.camera.generate_frames(),
            mimetype="multipart/x-mixed-replace; boundary=frame",
        )

    def start(self):
        self.app.run(host="0.0.0.0", port=self.port, threaded=True)
