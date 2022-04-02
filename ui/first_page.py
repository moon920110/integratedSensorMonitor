from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QComboBox, QLabel, QLineEdit
from PyQt5.QtCore import Qt


class FirstPageWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        next_btn = QPushButton("Start Recording")
        clr_btn = QPushButton("Clear Memory")
        quit_btn = QPushButton("Quit")

        partc_label = QLabel('Participant number', self)
        partc_label.setAlignment(Qt.AlignVCenter)
        partc_line = QLineEdit(self)

        partc_hbox = QHBoxLayout()
        partc_hbox.addStretch(1)
        partc_hbox.addWidget(partc_label)
        partc_hbox.addWidget(partc_line)
        partc_hbox.addStretch(1)

        game_label = QLabel('Game Genre', self)
        game_label.setAlignment(Qt.AlignVCenter)

        game_cb = QComboBox(self)
        game_cb.addItem('Racing')
        game_cb.addItem('Horror')
        game_cb.addItem('Bored')
        game_cb.addItem('Relaxed')

        game_hbox = QHBoxLayout()
        game_hbox.addStretch(1)
        game_hbox.addWidget(game_label)
        game_hbox.addWidget(game_cb)
        game_hbox.addStretch(1)

        music_label = QLabel('Music Genre', self)
        music_label.setAlignment(Qt.AlignVCenter)

        music_cb = QComboBox(self)
        music_cb.addItem('No BGM')
        music_cb.addItem('Original BGM')
        music_cb.addItem('Exciting BGM')
        music_cb.addItem('Anxious BGM')
        music_cb.addItem('Depressed BGM')
        music_cb.addItem('Relaxed BGM')

        music_hbox = QHBoxLayout()
        music_hbox.addStretch(1)
        music_hbox.addWidget(music_label)
        music_hbox.addWidget(music_cb)
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
