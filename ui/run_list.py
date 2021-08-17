from typing import List
from operator import attrgetter
from PyQt5.QtWidgets import QApplication, QLabel, QGridLayout, QPushButton
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal
import sys
from functools import partial
from controller.run_controller import RunProcess
from controller import RunConfigurationCRUD, RunResultCRUD
from model import RunConfiguration, DatabaseHandler, RunResult

DB = DatabaseHandler.get_instance()


class RunListWidget(QtWidgets.QWidget):
    """
    The RunListWidget class is an extension of the QWidget class and contains
    UI elements related to the Run List area
    SRS requirements: SRS[5], SRS[6], SRS[64], SRS[76], SRS[77]
    """

    # Signal intended to propagate to the RunContentTabbedWidget class to
    # display the RunDetailedView widget. Signal chain is initiated by RunResult class below.
    # Signal passes along the run_name and timestamp of the selected Run Result
    displayResult: pyqtSignal = pyqtSignal(str, str, object)

    def __init__(self, parent: QtWidgets.QWidget = None,
                 *, add_function: callable = None):
        super().__init__(parent)

        # Create layout
        self.layout: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout(self)

        # Create RunListTable and Add Button widgets
        self.run_list_table: RunListTable = RunListTable(self)
        self.add_button: QtWidgets.QPushButton = QtWidgets.QPushButton("Add", self)

        # Connect callbacks to signals
        self.run_list_table.displayResult.connect(self.displayResult)
        self.add_button.clicked.connect(add_function)

        # Add widgets to layout
        self.layout.addWidget(self.run_list_table)
        self.layout.addWidget(self.add_button)

    # Callback function connected to RunListTable displayResult signal
    # Emits this class's displayResult signal to notify RunContentTabbed widget
    # to invoke RunDetailedView
    def display_result(self, run_name: str, timestamp: str, run_process):
        self.displayResult.emit(run_name, timestamp, run_process)


class RunListTable(QtWidgets.QTableWidget):
    """
        The RunListTable class is an extension of the QTable widget class, and is
        intended to provide a list of all available Run Configurations. From this widget,
        Runs can be executed, suspended, or terminated.
        SRS requirements: SRS[6], SRS[64], SRS[76], SRS[77]
    """
    displayResult: pyqtSignal = pyqtSignal(str, str, object)

    def __init__(self, parent: QtWidgets.QWidget = None):
        super().__init__(parent)

        # Read all stored run configs
        self.run_list: List[RunConfiguration] = RunConfigurationCRUD.get_instance().read_all_run_configurations()

        # For every run configuration, a Run Process (see controller/run_controller.py) is created
        self.run_processes: List[RunProcess] = list()
        self.run_process_indirect: List[int] = list()

        if self.run_list:
            for run_configuration in self.run_list:
                self.run_processes.append(RunProcess(run_configuration))
                self.run_process_indirect.append(len(self.run_process_indirect))

        # Whenever the RunConfigurationCRUD emits a dataChanged signal, the update_data
        # callback is called.
        RunConfigurationCRUD.get_instance().dataChanged.connect(self.update_data)

        # Configure table columns and rows
        self.setColumnCount(4)
        self._horizontalLabels = [
            "Name",
            "Description",
            "Result"
        ]
        self.setHorizontalHeaderLabels(self._horizontalLabels)
        self.horizontalHeader().sectionClicked.connect(lambda x: self.sort_runs(reverse=not self.reverse))

        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

        # Parameter used by sort_runs()
        self.reverse = False
        self.sort_runs("_run_name")

    def sort_runs(self, key: str = "_run_name", reverse: bool = False):
        self.reverse = reverse
        self.update_data(key)

    # Used to initialize table contents and is intended to be called whenever
    # RunConfigurationCRUD emits a dataChanged signal.
    def update_data(self, key: str = "_run_name"):

        if key not in ("_id", "_run_name", "description"):
            raise ValueError(f"Bad sort key {key}")

        # Remove all current rows
        for i in range(len(self.run_list)):
            self.removeRow(0)
        self.clear()

        # Pull _id, name, description of all Run Configurations
        self.run_list = RunConfigurationCRUD.get_instance().read_all_run_configurations()

        # Adds a RunProcess object to list self.run_processes. Does a redudancy check to
        # make sure no duplicate RunProcesses are added
        if self.run_list:
            for run_configuration in self.run_list:
                if run_configuration.get_run_name() not in [process._run_config.get_run_name() for process in
                                                            self.run_processes]:
                    self.run_processes.append(RunProcess(run_configuration))
                    self.run_process_indirect.append(len(self.run_process_indirect))

        self.run_process_indirect.sort(key=lambda d: getattr(self.run_list[d], key), reverse=self.reverse)
        self.setHorizontalHeaderLabels(["Name", "Description", "Result", ""])
        for i in range(len(self.run_list)):
            self.insertRow(i)
            name_label = QtWidgets.QLabel(self.run_list[self.run_process_indirect[i]].get_run_name(), self)
            desc_label = QtWidgets.QLabel(self.run_list[self.run_process_indirect[i]].get_run_description(), self)
            control_widget = RunControlWidget(self.run_process_indirect[i], parent=self)
            self.setCellWidget(i, 0, name_label)
            self.setCellWidget(i, 1, desc_label)
            print(i, self.run_list[self.run_process_indirect[i]].get_run_name())
            run_result_widget = RunResultWidget(self.run_list[self.run_process_indirect[i]].get_run_name(),
                                                self.run_process_indirect[i], parent=self)
            run_result_widget.displayResult.connect(self.display_result)
            self.setCellWidget(i, 2, run_result_widget)
            self.setCellWidget(i, 3, control_widget)

    # Callback function that emits this class's displayResult signal
    def display_result(self, run_name: str, timestamp: str, run_process_index: int):
        self.parent().displayResult.emit(run_name, timestamp, self.run_processes[run_process_index])


class RunResultWidget(QtWidgets.QWidget):
    """
    The RunResultWidget is an extension of QWidget, and is intended for placement inside the
    Run Result column of the RunListTable widget. Displays clickable timestamps for every Run Result
    associated with a Run Configuration. Clicking a timestamp displays the Run Detailed View associated
    with the run result.
    SRS requirements: SRS[6].d, SRS[76], SRS[77]
    """

    # Signal emitted when a timestamp is clicked. Passes along the Run Configuration name
    # associated with it and the actual timestamp. This allows the proper Run Result to be
    # queried from the db by receiving widgets.
    displayResult: pyqtSignal = pyqtSignal(str, str, int)

    def __init__(self, run_name: str, run_process_index: int, parent: QtWidgets.QWidget = None):
        super().__init__(parent)

        # The name of the run that is associated with all the run result timestamps displayed
        # by this widget
        self._run_name: str = run_name

        # The index of the Run Process associated with this run configuration
        self.run_process_index: int = run_process_index

        # Retrieve all Run Results associated with given run name and create button
        # with timestamp as the label for each run result.
        self._run_results: List[RunResult] = RunResultCRUD.get_instance().read_run_results(self._run_name)
        self._layout: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout()
        if self._run_results:
            for run_result in self._run_results:
                result_button = QPushButton(run_result.get_timestamp(), self, flat=True)
                result_button.adjustSize()
                # Connect button to display result callback
                result_button.clicked.connect(partial(self.display_result, run_name,
                                                      run_result.get_timestamp(), self.run_process_index))
                self._layout.addWidget(result_button)
        else:
            self._layout.addWidget(QPushButton('No Results', flat=True))
        self.setLayout(self._layout)

        # Connect this widget to RunResultCRUD dataChanged signal. This instructs the widget
        # to redraw its list of results.
        RunResultCRUD.get_instance().dataChanged.connect(self.update_data)

    # Intended as a callback for clicks on timestamp buttons. Emits this class's displayResult
    # signal. Emitting this signal is intended to start a chain of signal emissions that propagate
    # from this widget, up through its parent widgets, terminating in the RunContentTabbedWidget.
    def display_result(self, run_name: str, timestamp: str, index: int):
        self.displayResult.emit(run_name, timestamp, self.run_process_index)

    # Intended as a callback for the RunResultCRUD dataChanged signal. Redraws this widgets
    # list of timestamps
    def update_data(self):
        # Remove all widgets
        for i in reversed(range(self._layout.count())):
            self._layout.itemAt(i).widget().setParent(None)

        # Retrieve all RunResults associated with given run name and create timestamp
        # button for each
        self._run_results = RunResultCRUD.get_instance().read_run_results(self._run_name)
        for run_result in self._run_results:
            result_button = QPushButton(run_result.get_timestamp(), self, flat=True)
            result_button.clicked.connect(partial(self.display_result, self._run_name, run_result.get_timestamp()))
            self._layout.addWidget(result_button)


class RunControlWidget(QtWidgets.QWidget):
    """
        The RunControlWidget class is an extension of the QWidget class and is intended for placement
        in the Control column of the RunListTableWidget. Each run control widget contains a play, pause, and stop
        QPushButton that is intended to control execution of the RunProcess associated with it.
        SRS requirements: SRS[6].e
    """

    def __init__(self, row: int, parent: QtWidgets.QWidget = None):
        super().__init__(parent)
        # Lets the widget know which row of the RunListTable it is placed in (consider finding replacement for this).
        # Uses this index to access the appropriate RunProcess in the list of RunProcesses contained in the
        # RunListTableWidget
        self.row = row
        layout = QtWidgets.QHBoxLayout(self)

        # Create play, pause, stop buttons and connect to appropriate callback
        self.play_button = QtWidgets.QPushButton("Play", self)
        self.pause_button = QtWidgets.QPushButton("Pause", self)
        self.stop_button = QtWidgets.QPushButton("Stop", self)
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
        self.get_run_process().play_run()

    # Pause button callback
    def pause(self):
        self.get_run_process().pause_run()

    # Stop button callback
    def stop(self):
        self.get_run_process().stop_run()

    # Accesses the appropriate run process in RunListTableWidget.
    # Consider placing run processes in this widget?
    def get_run_process(self):
        return self.parent().parent().run_processes[self.row]


if __name__ == "__main__":
    app = QApplication(sys.argv)
    qb = RunListTable()
    qb.show()
    sys.exit(app.exec_())
