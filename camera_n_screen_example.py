# VScode issue
import sys
import time
sys.path.append(".")

import ffmpeg
import os

from Parts.screen import ScreenRecorder
from Parts.camera import WebcamRecorder

webcam_re = WebcamRecorder()
screen_re = ScreenRecorder()

screen_re.select_screen_to_record(1, left=0, top=0, width=1920, height=1080)

webcam_re.record()
screen_re.record()

for i in range(5):
    print(i)
    time.sleep(0.8)

webcam_re.stop()
screen_re.stop()
screen_re.save(file_name='vid')
webcam_re.save(file_name='cam')
