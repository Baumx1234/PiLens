import argparse
import signal
import time
import threading

from camera_controller import CameraController
from mjpeg_stream_server import MJpegStreamServer


def main():
    try:
        # Parse command line arguments
        parser = argparse.ArgumentParser(
            description="Timelapse camera with MJPEG stream server"
        )
        parser.add_argument(
            "--output",
            type=str,
            default="/home/daniel/growcam/images",
            help="Base output directory",
        )
        parser.add_argument("--width", type=int, default=1024, help="Video-Width")
        parser.add_argument("--height", type=int, default=768, help="Video-Height")
        parser.add_argument("--fps", type=int, default=30, help="Frame-Rate")
        parser.add_argument("--port", type=int, default=5000, help="Stream-Port")
        parser.add_argument(
            "--interval",
            type=int,
            default=300,
            help="Capture-Interval in seconds",
        )
        parser.add_argument(
            "--format",
            default="jpg",
            choices=["jpg", "png"],
            help="Image-Save-Format",
        )
        args = parser.parse_args()

        # Initialize the camera controller and MJPEG stream server
        camera = CameraController(
            base_output_dir=args.output,
            frame_rate=args.fps,
            video_size=(args.width, args.height),
            still_interval=args.interval,
            save_mode=args.format,
        )
        stream_server = MJpegStreamServer(camera_controller=camera, port=args.port)

        # Start the camera and MJPEG stream server in separate threads
        flask_thread = threading.Thread(target=stream_server.start, daemon=True)
        timelapse_thread = threading.Thread(target=camera.start_timelapse_loop)

        flask_thread.start()
        timelapse_thread.start()

        # Register signal handlers to stop the application
        def signal_handler(sig, frame):
            print("Signal received. Stopping Application...")
            camera.stop()

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Wait for the threads to finish
        while timelapse_thread.is_alive():
            time.sleep(0.5)

    except Exception as e:
        print(f"Fatal error: {e}")
    finally:
        camera.stop()
        timelapse_thread.join()
        print("Application stopped")


if __name__ == "__main__":
    main()
