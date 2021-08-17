from typing import List, Optional
# TODO update relevant __init__ files
from model import RunConfiguration, RunState, RunResult, ScanState, TimeFormat
from controller import RunConfigurationCRUD
from controller.run_result_controller import RunResultCRUD
from controller.scan_controller import ScanProcess


class RunProcess:
    """
        The RunProcess class is responsible for managing the executing of its ScanProcesses,
        modifying the run's state, and making updates to the database based on the changes it makes.
        SRS requirements: SRS[48], SRS[49], SRS[50], SRS[51], SRS[52]
    """

    def __init__(self, run_config: RunConfiguration):
        # RunConfiguration associated with this RunProcess
        self._run_config: RunConfiguration = run_config
        # RunResult and RunConfiguration CRUDs for updating
        self._run_config_crud: RunConfigurationCRUD = RunConfigurationCRUD.get_instance()
        self._run_result_crud: RunResultCRUD = RunResultCRUD.get_instance()

        # These are initialized when play is clicked in play_run()
        self._run_result: Optional[RunResult] = None
        self._scan_processes: Optional[List[ScanProcess]] = list()

    # Starts all ScanProcesses in the Run also used to initialize _run_result and _scan_processes variables
    def play_run(self):
        state = self._run_config.get_run_state()

        # Creates RunResult and Scan processes only if the RunConfiguration is in the CONFIGURED state.
        # See RunState in model/State for all states
        if state == RunState.CONFIGURED.value or state == RunState.TERMINATED.value:
            # Create RunResult and place in db
            self._run_result = RunResult(TimeFormat.now(), self._run_config)
            self._run_result_crud.create_run_result(self._run_result)
            # Create ScanProcess for each ScanConfiguration contained in given RunConfiguration
            # Also connects the finished signal of the underlying process to a callback which checks
            # if all scans are complete
            for scan in self._run_config.get_scan_configurations():
                sp = ScanProcess(scan, self._run_result)
                self._scan_processes.append(sp)
                # Note: Should always be connected after ScanProcess is instantiated
                sp.get_process().finished.connect(self.check_terminated)

        # Executes ScanProcesses only if the Run is INACTIVE or CONFIGURED
        if state == RunState.INACTIVE.value or state == RunState.CONFIGURED.value:
            # Upon execution set run_state to ACTIVE, update the RunConfiguration in db,
            # and execute every ScanProcess
            for scan_process in self._scan_processes:
                self._run_config.set_run_state(RunState.ACTIVE.value)
                self._run_config_crud.update_run_configuration(self._run_config)
                scan_process.play_scan()

    # Pauses execution of all ScanProcesses and modifies RunConfiguration state
    def pause_run(self):
        state = self._run_config.get_run_state()
        # Can only pause if RunConfiguration state is ACTIVE. Changes state to INACTIVE.
        # Updates the db with this change. Pauses ScanProcesses
        if state == RunState.ACTIVE:
            for scan_process in self._scan_processes:
                self._run_config.set_run_state(RunState.INACTIVE.value)
                self._run_config_crud.update_run_configuration(self._run_config)
                scan_process.pause_scan()
            # Updates RunResult in db
            self._run_result_crud.update_run_result(self._run_result)

    # Terminates all ScanProcesses
    def stop_run(self):
        state = self._run_config.get_run_state()
        # Only if state is ACTIVE (should possible include INACTIVE?)
        if state == RunState.ACTIVE.value or state == RunState.INACTIVE:
            for scan_process in self._scan_processes:
                self._run_config.set_run_state(RunState.TERMINATED.value)
                self._run_config_crud.update_run_configuration(self._run_config)
                scan_process.stop_scan()
            self._run_result_crud.update_run_result(self._run_result)

    # Callback called upon the completion of a scan.
    # Checks if all scans are finished and if so changes state to TERMINATED
    def check_terminated(self):
        for scan_process in self._scan_processes:
            if scan_process.get_state() != ScanState.TERMINATED.value:
                return
        self._run_config.set_run_state(RunState.TERMINATED.value)
        self._run_config_crud.update_run_configuration(self._run_config)

    def get_scan_process(self, i: int):
        if self._scan_processes:
            return self._scan_processes[i]
