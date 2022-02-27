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
from parts.gsr import run_E4streaming, stop_E4streaming

deviceID = 'CD36CD'     # E4 wristband device id.   ex) 'A02088'

p_folder = './data/p43_0'     # save folder


if not os.path.exists(p_folder):
    os.makedirs(p_folder)


# Start E4 streaming
e4_thread = threading.Thread(target=run_E4streaming, args=(deviceID,))
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
        stop_E4streaming(p_folder)
        break