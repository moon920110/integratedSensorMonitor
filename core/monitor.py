import os
import time
import threading


class Monitor:
    def __init__(self, resolution=60):
        self.resolution = resolution
        self.parts = []

    def add_part(self, part, device):
        t = threading.Thread(target=part.stream)
        t.daemon = True
        entry = {'part': part, 'thread': t, 'device': device}

        self.parts.append(entry)

    def ready_parts(self):
        for p in self.parts:
            p['part'].ready()
        print("All parts are ready to record")

    def stream(self):
        for p in self.parts:
            p['thread'].start()

        time.sleep(1)
        print("All parts start streaming")

    def start_record(self):
        for p in self.parts:
            p['part'].record()

    def stop_record(self):
        for p in self.parts:
            p['part'].stop_record()

    def save_data(self, save_path):
        if not os.path.exists(save_path):
            os.mkdir(save_path)
        for p in self.parts:
            p['part'].save_data(save_path)

    def check_connection(self):
        dead_list = []
        for p in self.parts:
            if not p['thread'].is_alive():
                dead_list.append(p['device'])
        return dead_list

    def get_device_list(self):
        devices = []
        for p in self.parts:
            devices.append(p['device'])
        return devices

    def pause_recording(self):
        pass

    def resume_recording(self):
        pass

    def terminate(self):
        for p in self.parts:
            p['part'].terminate()
            p['thread'].join()
        print('terminate all devices')

    def clear(self):
        for p in self.parts:
            p['part'].clear()
        print('clear memory of all devices')