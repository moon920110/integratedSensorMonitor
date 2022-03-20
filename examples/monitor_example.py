import time
import os

from core.monitor import Monitor
from parts.gsr import GSR
from parts.eeg import EEG
from parts.gaze import Gaze
from parts.camera import WebcamRecorder
from parts.screen import ScreenRecorder

monitor = Monitor()

gsr = GSR('CD36CD')
eeg = EEG()
gaze = Gaze()
webcam = WebcamRecorder(camera_index=0)
screen = ScreenRecorder(monitor_num=1, left=0, top=0, width=3840, height=2160)

print("Instances are generated")

monitor.add_part(eeg)
monitor.add_part(gsr)
monitor.add_part(gaze)
monitor.add_part(webcam)
monitor.add_part(screen)

print("parts are added")

monitor.ready_parts()
monitor.stream()

time.sleep(3)

print("Start recording")
monitor.start_record()

time.sleep(10)

path = '../data'
if not os.path.exists(path):
    os.mkdir(path)
monitor.save_data(path)
