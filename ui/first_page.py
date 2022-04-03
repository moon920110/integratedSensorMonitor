from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QComboBox, QLabel, QLineEdit, QMessageBox
from PyQt5.QtCore import Qt, QCoreApplication


class FirstPageWidget(QWidget):
    def __init__(self, gtr, cs, monitor):
        super().__init__()
        self.monitor = monitor
        self.partc_line = None
        self.game_cb = None
        self.music_cb = None

        self.cs = cs
        self.gtr = gtr

        self.init_ui()

    def init_ui(self):
        next_btn = QPushButton("Start Recording")
        next_btn.clicked.connect(self.show_popup)
        clr_btn = QPushButton("Clear Memory")
        clr_btn.clicked.connect(self.clear_memory)
        quit_btn = QPushButton("Quit")
        quit_btn.clicked.connect(self.quit_monitor)

        partc_label = QLabel('Participant number', self)
        partc_label.setAlignment(Qt.AlignVCenter)
        self.partc_line = QLineEdit(self)

        partc_hbox = QHBoxLayout()
        partc_hbox.addStretch(1)
        partc_hbox.addWidget(partc_label)
        partc_hbox.addWidget(self.partc_line)
        partc_hbox.addStretch(1)

        game_label = QLabel('Game Genre', self)
        game_label.setAlignment(Qt.AlignVCenter)

        self.game_cb = QComboBox(self)
        self.game_cb.addItem('Exited')
        self.game_cb.addItem('Horror')
        self.game_cb.addItem('Bored')
        self.game_cb.addItem('Relaxed')

        game_hbox = QHBoxLayout()
        game_hbox.addStretch(1)
        game_hbox.addWidget(game_label)
        game_hbox.addWidget(self.game_cb)
        game_hbox.addStretch(1)

        music_label = QLabel('Music Genre', self)
        music_label.setAlignment(Qt.AlignVCenter)

        self.music_cb = QComboBox(self)
        self.music_cb.addItem('No-BGM')
        self.music_cb.addItem('Original-BGM')
        self.music_cb.addItem('Excited-BGM')
        self.music_cb.addItem('Anxious-BGM')
        self.music_cb.addItem('Depressed-BGM')
        self.music_cb.addItem('Relaxed-BGM')

        music_hbox = QHBoxLayout()
        music_hbox.addStretch(1)
        music_hbox.addWidget(music_label)
        music_hbox.addWidget(self.music_cb)
        music_hbox.addStretch(1)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(clr_btn)
        hbox.addWidget(next_btn)
        hbox.addWidget(quit_btn)
        hbox.addStretch(1)

        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(partc_hbox)
        vbox.addLayout(game_hbox)
        vbox.addLayout(music_hbox)
        vbox.addStretch(3)
        vbox.addLayout(hbox)
        vbox.addStretch(1)

        self.setLayout(vbox)

    def clear_memory(self):
        self.monitor.clear()
        self.cs.change_status.emit('The memory of all devices has been cleared')

    def show_popup(self):
        reply = QMessageBox.question(
            self,
            'Confirm',
            f'Are all the information correct?\n\n'
            f'Participant: {self.partc_line.text()}\n'
            f'Game Genre: {self.game_cb.currentText()}\n'
            f'Music Genre: {self.music_cb.currentText()}'
        )

        if reply == QMessageBox.Yes:
            self.gtr.go_to_record_page.emit()
        else:
            return False

    def quit_monitor(self):
        self.monitor.terminate()
        QCoreApplication.instance().quit()
