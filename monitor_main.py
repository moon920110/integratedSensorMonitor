import sys
import time

from core.monitor import Monitor
from parts.gsr import GSR
from parts.eeg import EEG
from parts.camera import WebcamRecorder
from parts.screen import ScreenRecorder
from PyQt5.QtWidgets import QApplication
from ui.ui_window import UIWindow


def main():
    monitor = Monitor()
    gsr = GSR('CD36CD')
    eeg = EEG()
    webcam = WebcamRecorder(camera_index=0)
    screen = ScreenRecorder(monitor_num=1, left=0, top=0, width=3840, height=2160)

    print('Instances are generated')

    monitor.add_part(eeg, 'eeg')
    print('eeg is added')
    monitor.add_part(gsr, 'gsr')
    print('gsr is added')
    monitor.add_part(webcam, 'webcam')
    print('webcam is added')
    monitor.add_part(screen, 'screen')
    print('screen is added')

    monitor.ready_parts()
    time.sleep(1)
    monitor.stream()

    ui = QApplication(sys.argv)
    ex = UIWindow(monitor)
    sys.exit(ui.exec_())


if __name__ == '__main__':
    main()
