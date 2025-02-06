from datetime import datetime
import os
import threading
import time

import cv2
from picamera2 import Picamera2
from picamera2.allocators import PersistentAllocator


class CameraController:
    def __init__(
        self,
        base_output_dir: str,
        frame_rate: int,
        video_size: tuple,
        still_interval: int,
        save_mode: str,
    ):
        # Initialize the camera controller with output directory, frame rate, and video size
        self.base_output_dir = base_output_dir
        self.picam2 = Picamera2(allocator=PersistentAllocator())
        self.lock = threading.Lock()
        self.still_interval = still_interval
        self.save_mode = save_mode
        self._running = False

        # Configure the preview settings for the camera
        self.preview_config = self.picam2.create_preview_configuration(
            {
                "size": video_size,
                "format": "RGB888",
            },
            controls={"FrameRate": frame_rate},
        )

        # Configure the still image settings for the camera
        self.still_config = self.picam2.create_still_configuration(
            {"size": self.picam2.sensor_resolution}
        )

        # Apply the preview configuration and start the camera
        self.picam2.configure(self.preview_config)
        self.picam2.start()
        # Allow the camera to warm up
        time.sleep(2)

    def capture_highres_image(self):
        # Capture a high-resolution image and save it to the output directory
        day_dir = self.create_day_directory()
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_path = os.path.join(
            day_dir, f"photo_{timestamp}.{self.save_mode}"
        )
        with self.lock:
            self.picam2.switch_mode_and_capture_file(
                self.still_config, file_path
            )
        print(f"Captured image: {file_path}")

    def generate_frames(self):
        # Generate frames for the MJPEG stream
        while self._running:
            with self.lock:
                frame = self.picam2.capture_array()
            _, buffer = cv2.imencode(".jpg", frame)
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n"
                + buffer.tobytes()
                + b"\r\n"
            )

    def start_timelapse_loop(self):
        self._running = True
        while self._running:
            start_time = time.time()
            try:
                self.capture_highres_image()
            except Exception as e:
                print(f"Error capturing high resolution image: {e}")
            elapsed = time.time() - start_time
            sleep_time = max(self.still_interval - elapsed, 1)
            time.sleep(sleep_time)

    def create_day_directory(self) -> str:
        # Create a directory for the current day to store images
        os.makedirs(self.base_output_dir, exist_ok=True)
        day_folder = datetime.now().strftime("%Y-%m-%d")
        day_path = os.path.join(self.base_output_dir, day_folder)
        os.makedirs(day_path, exist_ok=True)
        return day_path

    def stop(self):
        self._running = False
        self.picam2.stop()
        print("Camera stopped")
