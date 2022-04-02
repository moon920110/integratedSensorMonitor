import sys

import keyboard
from core.monitor import Monitor
from parts.gsr import GSR
from parts.eeg import EEG
# from parts.camera import WebcamRecorder
# from parts.screen import ScreenRecorder
from PyQt5.QtWidgets import QApplication
from ui.ui_window import UIWindow


def main():
    monitor = Monitor()
    # gsr = GSR('CD36CD')
    # eeg = EEG()
    # webcam = WebcamRecorder(camera_index=0)
    # screen = ScreenRecorder(monitor_num=1, left=0, top=0, width=3840, height=2160)

    print('Instances are generated')

    # monitor.add_padded')
    # monitor.add_part(eeg)
    # print('eeg is added')
    # monitor.add_part(webcam)
    # print('webcam is added')
    # monitor.add_part(screen)
    # print('screen is added')

    monitor.ready_parts()
    monitor.stream()

    partc = None
    exp_num = None
    data_path = 'D:/Research/Game/Game_music/dataset/game_music_emotion_exp'

    ui = QApplication(sys.argv)
    ex = UIWindow()
    sys.exit(ui.exec_())
    # while True:
    #     # new record
    #     if keyboard.is_pressed('n'):
    #         print("New experiment")
    #         partc = input("Participant num:")
    #         print(f"Participant: {partc}")
    #         exp_num = input("Exp num:")
    #         print(f"Experiment number: {exp_num}")
    #
    #     # start record
    #     if keyboard.is_pressed('r'):
    #         monitor.start_record()
    #     # stop record
    #     if keyboard.is_pressed('q'):
    #         monitor.stop_record()
    #     # save record
    #     if keyboard.is_pressed('o'):
    #         monitor.save_data()


if __name__ == '__main__':
    main()