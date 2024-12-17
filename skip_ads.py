"""
Take photo and if "skip" but not "skip in" text detected then send select action to Roku TV
"""
import os
import time
import logging
import sys
import requests
import pytesseract
import cv2


pytesseract.pytesseract.tesseract_cmd = (
    "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def take_pic(cap, save_pic_path):
    """Take Picture with webcam and return frame"""
    _, frame = cap.read()
    if save_pic_path != "":
        logging.debug("Saving Image to path: %s", save_pic_path)
        cv2.imwrite(save_pic_path, frame)
    return frame


def main():
    """Take picture and search for skip but not skip in, if found send select to tv"""
    roku_ip = os.environ.get("ROKU_IP", "")
    if roku_ip == "":
        logging.error("Set ROKU_IP env var to tv IP address")
        sys.exit(1)
    endpoint = f"http://{roku_ip}:8060/keypress/Select"
    logging.debug("ROKU_IP: %s, ROKU ENDPOINT: %s", roku_ip, endpoint)
    save_pic_path = ""
    save_pic = os.environ.get("SAVE_PIC", "false")
    if save_pic.lower() in ["true", "1", "yes", "y"]:
        save_pic_path = os.getcwd() + "\\capture_image.jpg"
        logging.debug("Save pic enabled, path: %s", save_pic_path)
    keyword = "skip"
    keyword_exclude = "in"
    cap = cv2.VideoCapture(0)
    try:
        while True:
            frame = take_pic(cap, save_pic_path)
            text = pytesseract.image_to_string(frame).lower()
            logging.debug("ALL TEXT FOUND IN IMAGE: %s", text)
            if keyword.lower() in text and keyword_exclude.lower() not in text:
                logging.info("The text %s was found in the image", keyword)
                response = requests.post(endpoint, timeout=10)
                if response.status_code == 200:
                    logging.info("Button press command sent successfully.")
                    logging.debug("Waiting 3 seconds to debounce...")
                    time.sleep(3)
                else:
                    logging.warning(
                        "Error: Failed to send to TV: %s", response.status_code
                    )
            elif keyword.lower() in text and keyword_exclude.lower() in text:
                logging.info("%s and %s found in image.", keyword, keyword_exclude)
            else:
                logging.info("The text %s was not found in the image.", keyword)
    except KeyboardInterrupt:
        logging.info("Keyboard interrupt detected. Exiting the loop.")
    finally:
        cap.release()


if __name__ == "__main__":
    main()
