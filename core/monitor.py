import time
import threading


class Monitor:
    def __init__(self, resolution=60):
        self.resolution = resolution
        self.parts = []

    def add_part(self, part):
        t = threading.Thread(target=part.stream)
        t.daemon = True
        entry = {'part': part, 'thread': t}

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
        for p in self.parts:
            p['part'].save_data(save_path)

    def pause_recording(self):
        pass

    def resume_recording(self):
        pass

    def terminate(self):
        for p in self.parts:
            p['part'].terminate()