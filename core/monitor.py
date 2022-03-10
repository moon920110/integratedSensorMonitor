import time
import threading


class Monitor:
    def __init__(self, resolution):
        self.resolution = resolution
        self.parts = []

    def add_parts(self, part, threaded=False):
        entry = {}
        entry['part'] = part
        if threaded:
            t = threading.Thread(part.stream)
            t.daemon = True
            entry['thread'] = t

        self.parts.append(entry)

    def run(self):
        pass