from _thread import start_new_thread

from PyQt5 import QtWidgets

from ui import ToolContentTabbedWidget, RunContentTabbedWidget


class App(QtWidgets.QApplication):
    def __init__(self):
        super().__init__([])

        window = QtWidgets.QMainWindow()
        window.setWindowTitle("S.E.A. Tool")

        tabbed = QtWidgets.QTabWidget()
        tabbed.addTab(RunContentTabbedWidget(tabbed), "Run Area")
        tabbed.addTab(ToolContentTabbedWidget(tabbed), "Tool Area")

        window.setCentralWidget(tabbed)
        window.show()
        self.exec_()


if __name__ == "__main__":
    app = App()
