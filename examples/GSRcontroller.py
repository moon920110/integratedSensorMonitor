"""
2021-05-17
scijspirit@gmail.com

This script is basic code to control the stream data from E4 GSR devices.
E4 stream data can be synchronized by keyboard event.
"""
import os
import threading

import keyboard
from utils import keyboardMarker
from parts.gsr import GSR

deviceID = 'CD36CD'     # E4 wristband device id.   ex) 'A02088'

p_folder = './data/p43_0'     # save folder


if not os.path.exists(p_folder):
    os.makedirs(p_folder)


# Start E4 streaming
gsr = GSR('CD36CD')
e4_thread = threading.Thread(target=gsr.run_E4streaming)
e4_thread.setDaemon(True)
e4_thread.start()

# Mark start event
keyboardMarker('O')

while True:
    if keyboard.is_pressed('q'):
        print("Stop recording..")

        # Mark end event
        keyboardMarker('O')

        # Stop E4 streaming
        gsr.stop_E4streaming(p_folder)
        break