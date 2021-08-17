import psutil
from typing import Union, List
from PyQt5.QtCore import QProcess
from controller.run_result_controller import RunResultCRUD
from model import ScanState, ScanResult, TimeFormat, ScanConfiguration, RunResult


class ScanProcess:
    """
        The ScanProcess class is responsible for managing the execution of its QProcess
        which hosts the underlying tool's executable, modifying the scan's state, and making
        updates to the database based on the changes it makes.
        SRS requirements: SRS[53] - SRS[59]
        Currently unsatisfied SRS reqs: SRS[55], SRS[56].c, SRS[56].d, SRS[58]
    """

    def __init__(self, scan_config, run_result):
        # QProcess object used to execute underlying tools
        self._process: QProcess = QProcess()

        # Connect handlers to QProcess's readyStandardOutput and finished signals
        self._process.readyReadStandardOutput.connect(self.handle_stdout)
        # Note: Qt invokes callbacks in the order they are connected. Moving this
        # outside the constructor may create issues with state of runs and scans
        self._process.finished.connect(self.handle_finished)

        # Used to suspend, resume, terminate processes since these features are
        # not available with QProcess
        self._process_helper: Union[psutil.Process, None] = None

        # Assigned upon beginning of execution in play_scan
        self._pid: Union[int, None] = None

        # A handle to the RunResult object that should contain the ScanResult associated with this ScanProcess
        self._run_result: RunResult = run_result

        # Create ScanResult object for this process and add it to parent RunResult
        self._scan_config: ScanConfiguration = scan_config
        self._scan_result: ScanResult = ScanResult(scan_config)
        self._run_result.add_scan_result(self._scan_result)
        self._run_result_crud: RunResultCRUD = RunResultCRUD.get_instance()

        # Arguments that will be ingested by QProcess
        self._whitelist: List[str] = self._run_result.get_run_configuration().get_target().get_whitelist()
        self._tool_args: List[str] = self._scan_config.get_tool_configuration().get_arg_list() + self._whitelist

        # Path to executable
        self._tool_path: str = self._scan_config.get_tool_configuration().get_tool_path()

    # Executes the QProcess that will host the underlying tool's executable
    def play_scan(self):
        # Only executes if this is the Scan's first time being executed. The
        # self._process_helper variable is only assigned at this stage and is used
        # to tell if a scan needs to be executed for the first time or simply resumed.
        if self.get_state() == ScanState.INACTIVE.value and not self._process_helper:
            # Set state, start time, and update in db
            self._scan_config.set_scan_state(ScanState.ACTIVE.value)
            self._scan_result.set_scan_start_time(TimeFormat.now())
            self._run_result_crud.update_run_result(self._run_result)

            # Execute the underlying tool
            self._process.start(self._tool_path, self._tool_args)
            # Get the underlying tool's pid and pass on to process helper
            pid = self._process.processId()
            self._pid = pid if pid else None
            self._process_helper = psutil.Process(self._pid)

        # If the scan has been already initiated simply resume
        elif self.get_state() == ScanState.INACTIVE.value and self._process_helper:
            self._process_helper.resume()

    # Suspends process only if ACTIVE, changes Scan state, and updates db
    def pause_scan(self):
        if self.get_state() == ScanState.ACTIVE.value and self._process_helper:
            self._scan_config.set_scan_state(ScanState.INACTIVE.value)
            self._run_result_crud.update_run_result(self._run_result)
            self._process_helper.suspend()

    # Terminates process only if Scan has been initialized and is not already terminated or finished.
    # Sets scan state, sets end time, and updates db, sets pid to none.
    def stop_scan(self):
        if self._process_helper and self.get_state() != ScanState.TERMINATED.value:
            self._scan_config.set_scan_state(ScanState.TERMINATED.value)
            self._scan_result.set_scan_end_time(TimeFormat.now())
            self._run_result_crud.update_run_result(self._run_result)
            self._process_helper.terminate()
            self._pid = None

    # Callback function that receives stdOut of underlying tool and places in db.
    # Connected to self._process readyStandardOutput signal.
    def handle_stdout(self):
        data = self._process.readAllStandardOutput()
        data = bytes(data).decode('utf8')
        # Accumulates the output as it is received
        self._scan_result._formatted_scan_output += data
        self._run_result_crud.update_run_result(self._run_result)
        print(data)

    # Callback function connected to self._process finished signal.
    # Sets end time, updates db, sets pid to none
    def handle_finished(self):
        self._scan_result.set_scan_end_time(TimeFormat.now())
        self._scan_config.set_scan_state(ScanState.TERMINATED.value)
        self._run_result_crud.update_run_result(self._run_result)
        self._pid = None

    # Helper method for getting state of associated Scan state
    def get_state(self):
        return self._scan_config.get_scan_state()

    def get_process(self) -> QProcess:
        return self._process
