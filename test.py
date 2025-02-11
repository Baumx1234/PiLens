import time
from picamera2 import Picamera2, Preview
from datetime import datetime
import os


def main():
    BASE_OUTPUT_DIR = "/home/daniel/growcam/images"

    try:
        if not os.path.exists(BASE_OUTPUT_DIR):
            os.makedirs(BASE_OUTPUT_DIR)
    except Exception as e:
        print(f"Fehler beim Erstellen des Basisverzeichnisses: {e}")
        return

    try:
        picam2 = Picamera2()
        camera_config = picam2.create_still_configuration(
            main={"size": (3280, 2464)}
        )
        picam2.configure(camera_config)
        picam2.start()


        time.sleep(2)

        picam2.set_controls({
            "AwbEnable": False,
            "ColourGains": (1.27, 2.4)  # Passe diese Werte je nach Bedarf an
        })

    except Exception as e:
        print(f"Fehler bei der Initialisierung der Kamera: {e}")
        return

    try:
        print("Starte die Fotoaufnahme alle 5 Minuten...")
        while True:
            # Timestamp für den Dateinamen und den Tagesordner generieren
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            day_folder = datetime.now().strftime("%Y-%m-%d")

            # Tagesordner erstellen, falls er nicht existiert
            day_output_dir = os.path.join(BASE_OUTPUT_DIR, day_folder)
            if not os.path.exists(day_output_dir):
                os.makedirs(day_output_dir)

            # Dateipfad für das Foto
            file_path = os.path.join(day_output_dir, f"photo_{timestamp}.jpg")

            # Foto aufnehmen
            picam2.capture_file(file_path)
            print(f"Foto aufgenommen: {file_path}")
            metadata = picam2.capture_metadata()

            # AWB-Werte (Farbverstärkung) aus den Metadaten auslesen und drucken
            awb_gains = metadata.get("ColourGains")
            if awb_gains is not None:
                print("Automatisch ermittelte AWB-Gains:", awb_gains)
            else:
                print("Keine AWB-Informationen in den Metadaten gefunden.")

                # 5 Minuten warten
                time.sleep(30)  # 300 Sekunden = 5 Minuten
    except KeyboardInterrupt:
        print("Programm durch Benutzer beendet.")
    except Exception as e:
        print(f"Fehler bei der Fotoaufnahme: {e}")
    finally:
        picam2.stop()
        print("Kamera gestoppt.")


if __name__ == "__main__":
    main()
