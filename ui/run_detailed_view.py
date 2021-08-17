from PyQt5.QtWidgets import QWidget, QGridLayout
from ui import RunStatisticalDataTable, ScanResults

'''
@author Kenneth Ward
This file contains classes and code related to the "detailed view of a selected run"
'''


class RunDetailedView(QWidget):
    """
        The RunDetailedView class integrates the Statistical Data Table and the Scan Result areas.
        This class addresses the following SRS requirements:
        SRS[8]
    """

    def __init__(self, run_name: str = '', timestamp: str = '', run_process=None):
        super().__init__()

        # Make and set Window Title
        self._title: str = 'Run Details'
        self.setWindowTitle(self._title)

        # Integrate RunTable and Scan Results
        self._layout: QGridLayout = QGridLayout()

        if run_name and timestamp and run_process:
            # Add the Stat data table
            self._layout.addWidget(RunStatisticalDataTable(run_name, timestamp, run_process), 0, 0)
            # Add scan result tabs
            self._layout.addWidget(ScanResults(run_name, timestamp), 1, 0)
        else:
            # Add the Stat data table
            self._layout.addWidget(RunStatisticalDataTable(), 0, 0)
            # Add scan result tabs
            self._layout.addWidget(ScanResults(), 1, 0)
        self.setLayout(self._layout)
        self._run_result = None

# Testing driver
if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    widget = RunDetailedView()
    widget.setGeometry(300, 400, 600, 800)
    widget.show()

    sys.exit(app.exec_())
