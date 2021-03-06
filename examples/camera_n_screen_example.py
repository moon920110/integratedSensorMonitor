import time

import ffmpeg
import os

from parts.screen import ScreenRecorder
from parts.camera import WebcamRecorder

webcam_re = WebcamRecorder()
screen_re = ScreenRecorder(1, left=0, top=0, width=1920, height=1080)

screen_re.ready()

webcam_re.record()
screen_re.record()

for i in range(5):
    print(i)
    time.sleep(0.8)

webcam_re.stop()
screen_re.stop()
# screen_re.save(file_name='vid')
webcam_re.save(file_name='cam')
