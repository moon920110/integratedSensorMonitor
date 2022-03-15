import time
import os

from core.monitor import Monitor
from parts.gsr import GSR
from parts.eeg import EEG
from parts.gaze import Gaze

monitor = Monitor()

gsr = GSR('CD36CD')
eeg = EEG()
gaze = Gaze()

print("Instances are generated")

monitor.add_part(eeg)
monitor.add_part(gsr)
monitor.add_part(gaze)

print("parts are added")

monitor.ready_parts()
monitor.stream()

print("Start recording")
monitor.start_record()

######
time.sleep(10)
######

path = '../data'
if not os.path.exists(path):
    os.mkdir(path)
monitor.save_data(path)
