from PyQt5 import QtWidgets
from functools import partial

from ui import RunConfiguration, RunDetailedView, RunListWidget, XMLReport


class RunContentTabbedWidget(QtWidgets.QTabWidget):
    """
        The RunContentTabbedWidget is an extension of the QTabWidget class and contains three widgets:
        the RunListWidget, the RunDetailedView, and the RunConfiguration widget. Each widget is assigned its own tab
        SRS requirements: SRS[4]
    """
    def __init__(self, parent: QtWidgets.QWidget = None):
        super().__init__(parent)

        # Creates 3 widgets intended for placement in a tab
        self.run_list_widget: RunListWidget = RunListWidget(add_function=partial(self.switch_view, 1))
        self.run_details: RunDetailedView = RunDetailedView()
        self.run_configuration: RunConfiguration = RunConfiguration(accept_function=partial(self.switch_view, 0),
                                                                    cancel_function=partial(self.switch_view, 0))

        # Listens for displayResult signal emitted from RunResult widget contained in RunListWidget
        self.run_list_widget.displayResult.connect(self.display_result)

        #Add the 3 widgets to tabs
        self.addTab(self.run_list_widget, "Run List")
        self.addTab(self.run_configuration, "Run Configuration")
        self.addTab(self.run_details, "Run Details")
        self.addTab(XMLReport(self), "XML Report")
        self.show()

    # Switches current tab being displayed
    def switch_view(self, view: int):
        self.setCurrentIndex(view)

    # Called when RunResult widget emits displayResult signal.
    # Deletes empty Run Details tab, creates new one populated
    # with relevant run details. Switches tabs.
    def display_result(self, run_name: str, timestamp: str, run_process: object):
        self.widget(2).deleteLater()
        self.run_details = RunDetailedView(run_name, timestamp, run_process)
        self.addTab(self.run_details, "Run Details")
        self.switch_view(2)

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    r = RunContentTabbedWidget()
    app.exec_()
