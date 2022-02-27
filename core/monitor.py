import time


class Monitor:
    def __init__(self, resolution):
        self.resolution = resolution
        self.parts = None

    def add_parts(self, part, threaded=False):
        if threaded:

        self.parts.append(part)

    def run(self):
        pass