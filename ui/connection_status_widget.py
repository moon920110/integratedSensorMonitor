from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import QTimer


class ConnectionStatusWidget(QWidget):
    def __init__(self, monitor):
        super().__init__()
        self.monitor = monitor
        self.devices = {}
        for device in monitor.get_device_list():
            self.devices[device] = QLabel('Connected', self)
            self.devices[device].setStyleSheet('color: green;')

        self.cc_timer = QTimer(self)
        self.cc_timer.setInterval(1000)
        self.cc_timer.timeout.connect(self.check_connection)
        self.cc_timer.start()

        self.init_ui()

    def init_ui(self):
        vbox = QVBoxLayout()
        for device, status in self.devices.items():
            hbox = QHBoxLayout()
            hbox.addWidget(QLabel(f'{device}:', self))
            hbox.addWidget(status)
            vbox.addLayout(hbox)
        self.setLayout(vbox)

    def check_connection(self):
        lost_devices = self.monitor.check_connection()
        if len(lost_devices) > 0:
            for lost_device in lost_devices:
                self.devices[lost_device].setText('Lost connection')
                self.devices[lost_device].setStyleSheet('color: red;')
