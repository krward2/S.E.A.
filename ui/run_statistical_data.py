from PyQt5.QtWidgets import QWidget, QPushButton, QGridLayout, QTableWidget, QHeaderView, QLabel, QHBoxLayout
from typing import List
from model import RunResult
from controller.run_result_controller import RunResultCRUD

'''
@author Kenneth Ward
This file contains classes and code related to the Run Statistical Data Table
'''


class RunStatisticalDataTable(QTableWidget):
    """
        The RunStatisticalDataTable class creates a table with columns labelled as described in SRS[9]
        This class satisfies the following SRS requirements:
        SRS[9]
    """

    def __init__(self, run_name: str = '', timestamp: str = '', run_process=None):
        super().__init__()
        self._run_name: str = run_name
        self._timestamp: str = timestamp
        self.run_process = run_process

        # Make columns and column labels
        self.setColumnCount(7)
        self._headers: list = list(['Scan', 'Execution\nNumber', 'Start Time', ' End Time',
                                    ' Scanned IPs', 'Success/Failure', 'Control'])
        self.setHorizontalHeaderLabels(self._headers)

        # If run_name and timestamp are provided, populate table with ScanResults
        # associated with the RunResult having the run_name and timestamp given
        if run_name and timestamp and run_process:
            RunResultCRUD.get_instance().dataChanged.connect(self.update_data)
            self.update_data()
        # Else populate with dummy rows. (For demo purposes, maybe remove?)
        else:
            self._scan_results: List = list()
            self.example_rows()

        # Format table cells to stretch around Control Buttons and Header Labels
        header: QHeaderView = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header: QHeaderView = self.verticalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)

    # Populate table with dummy rows
    def example_rows(self):
        for i in range(20):
            self.insertRow(i)
            self.setCellWidget(i, 6, ControlButtonsWidget())

    # Intended to initialize table with Scan Results and act as a callback for
    # RunResultCRUD dataChanged signal
    def update_data(self):
        # Delete all rows
        for i in range(self.rowCount()):
            self.removeRow(0)
        self.clear()

        # reset column headers
        self._headers: list = list(['Scan', 'Execution\nNumber', 'Start Time', ' End Time',
                                    ' Scanned IPs', 'Success/Failure', 'Control'])
        self.setHorizontalHeaderLabels(self._headers)

        # Retrieve ScanResults associated with run_name and timestamp
        self.run_result = RunResultCRUD.get_instance().read_run_result(self._run_name, self._timestamp)
        self._scan_results = self.run_result.get_scan_results()

        # Add a row for each ScanResult and populate cells
        for row, scan_result in enumerate(self._scan_results):
            self.insertRow(row)

            scan = QLabel(scan_result.get_scan_name(), self)
            execution_number = QLabel(str(scan_result.get_scan_configuration().get_execution_number()), self)
            start_time = QLabel(scan_result.get_scan_start_time(), self)
            end_time = QLabel(scan_result.get_scan_end_time(), self)
            wl = self.get_whitelist_formatted()
            scanned_ips = QLabel(wl, self)
            execution_status = QLabel(str(scan_result.get_execution_status()), self)

            self.setCellWidget(row, 0, scan)
            self.setCellWidget(row, 1, execution_number)
            self.setCellWidget(row, 2, start_time)
            self.setCellWidget(row, 3, end_time)
            self.setCellWidget(row, 4, scanned_ips)
            self.setCellWidget(row, 5, execution_status)

            # Mostly for demo purposes. Want to show table with/without scans running
            if self.run_process.get_scan_process(row):
                self.setCellWidget(row, 6, ScanControlWidget(self.run_process.get_scan_process(row)))

    # Helper method for getting a string that places each whitelist ip on its own line
    def get_whitelist_formatted(self):
        whitelist = self.run_result.get_run_configuration().get_target().get_whitelist()
        wl = ''
        for ip in whitelist:
            wl += ip+'\n'
        return wl.strip()


class ControlButtonsWidget(QWidget):
    """
    The ControlButtonsWidget defines a widget of three buttons that appears in the RunTable widget.
    The ControlButtonsWidget class addresses SRS requirements:
    SRS[9].k
    """

    # TODO Add process control capability
    def __init__(self):
        super().__init__()
        # Labels used to identify the three buttons
        buttonLabels: list = list(['Play', 'Pause', 'Stop'])

        # Create layout for the widget
        self._layout: QGridLayout = QGridLayout()

        # Adds one button to the widget for each label in buttonLabels
        for row, label in enumerate(buttonLabels):
            self._layout.addWidget(QPushButton(label), 0, row)
        self.setLayout(self._layout)


class ScanControlWidget(QWidget):
    """
    The ScanControlWidget class is an extension of the QWidget class and is intended for placement
    in the Control column of the RunListTableWidget. Each run control widget contains a play, pause, and stop
    QPushButton that is intended to control execution of the RunProcess associated with it.
    SRS requirements:
    """

    def __init__(self, scan_process, parent: QWidget = None):
        super().__init__(parent)
        self.scan_process = scan_process
        layout = QHBoxLayout(self)

        # Create play, pause, stop buttons and connect to appropriate callback
        self.play_button = QPushButton("Play", self)
        self.pause_button = QPushButton("Pause", self)
        self.stop_button = QPushButton("Stop", self)
        self.play_button.clicked.connect(self.play)
        self.pause_button.clicked.connect(self.pause)
        self.stop_button.clicked.connect(self.stop)

        # Place buttons in layout
        layout.addWidget(self.play_button)
        layout.addWidget(self.pause_button)
        layout.addWidget(self.stop_button)
        self.show()

    # Play button callback
    def play(self):
        self.scan_process.play_scan()

    # Pause button callback
    def pause(self):
        self.scan_process.pause_scan()

    # Stop button callback
    def stop(self):
        self.scan_process.stop_scan()


# Testing driver
if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    widget = RunStatisticalDataTable()
    widget.setGeometry(300, 400, 600, 800)
    widget.show()

    sys.exit(app.exec_())
