from PyQt5.QtCore import pyqtSignal, QObject


class GoToRecordingPage(QObject):
    go_to_record_page = pyqtSignal()


class BackToFirstPage(QObject):
    back_to_first_page = pyqtSignal()


class ChangeStatus(QObject):
    change_status = pyqtSignal(str)
