import sys
from PyQt5.QtWidgets import QDesktopWidget, QMainWindow, QApplication, QStackedWidget

from ui.first_page import FirstPageWidget


class UIWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        widgets = QStackedWidget()
        firstpage_widget = FirstPageWidget()
        widgets.addWidget(firstpage_widget)

        self.setCentralWidget(widgets)
        self.change_status('Init')

        self.setWindowTitle("sensor signal collector")
        self.resize(400, 400)
        self._center()
        self.show()

    def change_status(self, status_msg):
        self.statusBar().showMessage(status_msg)

    def _center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()

        qr.moveCenter(cp)
        self.move(qr.topLeft())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = UIWindow()
    sys.exit(app.exec_())
