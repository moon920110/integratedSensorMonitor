from libs.tobii import tobii_research as tr

import os
import time
from datetime import datetime
import pandas as pd


class Gaze:
    def __init__(self, ):
        self.found_eyetrackers = tr.find_all_eyetrackers()
        self.my_eyetracker = None
        self.stream_data = None

        self.columns = ["time", "gaze_left", "gaze_right"]
        self.time = []
        self.gaze_left = []
        self.gaze_right = []

        self.start_checker = 0
        self.end_checker = 0
        self._recording = False

    def gaze_data_callback(self, gaze_data):
        # Print gaze points of left and right eye
        gaze_time = datetime.now()
        gaze_left = gaze_data['left_gaze_point_on_display_area']
        gaze_right = gaze_data['right_gaze_point_on_display_area']

        self.time.append(gaze_time)
        self.gaze_left.append(gaze_left)
        self.gaze_right.append(gaze_right)

        # time.sleep(5)

    def ready(self):
        if self.found_eyetrackers == ():
            print("Not connected tobii")
        else:
            self.my_eyetracker = self.found_eyetrackers[0]

            print("Connected Tobii")
            print("Address: " + self.my_eyetracker.address)
            print("Model: " + self.my_eyetracker.model)
            print("Name (It's OK if this is empty): " + self.my_eyetracker.device_name)
            print("Serial number: " + self.my_eyetracker.serial_number)

    ## stream
    def stream(self):
        if not self.my_eyetracker is None:
            self.my_eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, self.gaze_data_callback, as_dictionary=True)

    ## record
    def record(self):
        self._recording = True
        self.start_checker = datetime.now()

    def stop_record(self):
        self.end_checker = datetime.now()
        self.stream_data = pd.DataFrame()

        self.stream_data['time'] = self.time
        self.stream_data['gaze_left'] = self.gaze_left
        self.stream_data['gaze_right'] = self.gaze_right

        self.stream_data = self.stream_data[(self.stream_data.time >= self.start_checker) &
                                            (self.stream_data.time <= self.end_checker)]

        self._recording = False

        self.start_checker = 0
        self.end_checker = 0

    def terminate(self):
        self.my_eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, self.gaze_data_callback)

    def save_data(self, folder):
        if self._recording:
            self.stop_record()

        self.makedirs(folder)
        self.stream_data.to_csv(os.path.join(folder, "gaze.csv"), index=False)

    def makedirs(self, path):
        try:
            os.makedirs(path)
        except OSError:
            if not os.path.isdir(path):
                raise

def main():
    gaze = Gaze()
    gaze.ready()
    gaze.stream()
    print("stream")
    time.sleep(5)

    gaze.record()
    print("Recording ..")
    time.sleep(10)
    gaze.stop_record()
    print("Stop Recording")

    gaze.save_data(os.path.join(os.path.abspath(os.path.join(os.path.abspath("./"), os.pardir)), "save"))
    print("save")
    gaze.terminate()
    print("terminate")

if __name__ == "__main__":
    main()