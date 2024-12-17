"""
Take photo and if "skip" but not "skip in" text detected then send select action to Roku TV
"""

import os
import time
import sys
import requests
import pytesseract
import cv2


pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"


def take_pic(cap, save_pic_path):
    """Take Picture with webcam and return frame"""
    _, frame = cap.read()
    if save_pic_path != "":
        print("Saving Image to path: ", save_pic_path)
        cv2.imwrite(save_pic_path, frame)
    return frame


def main():
    """Take picture and search for skip but not skip in, if found send select to tv"""
    roku_ip = os.environ.get("ROKU_IP", "")
    if roku_ip == "":
        print("Set ROKU_IP env var to tv IP address")
        sys.exit(1)
    endpoint = f"http://{roku_ip}:8060/keypress/Select"
    print("ROKU_IP:", roku_ip, "ROKU ENDPOINT:", endpoint)
    save_pic_path = ""
    save_pic = os.environ.get("SAVE_PIC", "false")
    if save_pic.lower() in ["true", "1", "yes", "y"]:
        save_pic_path = os.getcwd() + "/capture_image.jpg"
        print("Save pic enabled, path: ", save_pic_path)
    keyword = "skip"
    keyword_exclude = "in"
    cap = cv2.VideoCapture(2)
    try:
        while True:
            frame = take_pic(cap, save_pic_path)
            text = pytesseract.image_to_string(frame).lower()
            print("ALL TEXT FOUND IN IMAGE: ", text)
            if keyword.lower() in text and keyword_exclude.lower() not in text:
                print("The text was found in the image", keyword)
                response = requests.post(endpoint, timeout=10)
                if response.status_code == 200:
                    print("Button press command sent successfully.")
                    print("Waiting 3 seconds to debounce...")
                    time.sleep(3)
                else:
                    print("ERROR SENDING TO TV")
            elif keyword.lower() in text and keyword_exclude.lower() in text:
                print(keyword, "and", keyword_exclude, "found in image.")
            else:
                print("The text", keyword, "was not found in the image.")
    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Exiting the loop.")
    finally:
        cap.release()


if __name__ == "__main__":
    main()
