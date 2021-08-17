from PyQt5.QtCore import QObject, pyqtSignal

from model import RunResult, ScanResult, DatabaseHandler


class RunResultCRUD(QObject):
    """
        A Singleton controller class responsible for CRUD operations on the Run Result collection,
        and for notifying relevant UI widgets of changes to data.
    """

    dataChanged: pyqtSignal = pyqtSignal()

    def __init__(self):
        super().__init__()
        if RunResultCRUD.__instance is not None:
            raise Exception('Only one instance of RunResultCRUD allowed.')
        else:
            self._DB: DatabaseHandler = DatabaseHandler.get_instance()

    # Contains the handle to the single instance
    __instance = None

    # Replaces the constructor as the method of obtaining an instance
    @staticmethod
    def get_instance():
        if RunResultCRUD.__instance is None:
            RunResultCRUD.__instance = RunResultCRUD()
            return RunResultCRUD.__instance
        else:
            return RunResultCRUD.__instance

    # Adds a new Run Result to the database
    def create_run_result(self, run_result: RunResult):
        result = self._DB.push_run_result(run_result.to_json())
        self.dataChanged.emit()
        return result.acknowledged, result.inserted_id if result.acknowledged else None

    # Returns the Run Result associated the given run_id
    def read_run_result(self, run_name: str, timestamp: str):
        result = self._DB.pull_run_result(run_name, timestamp)
        if result:
            return RunResult.from_json(result)

    #Reads all run results associated with a run of given name
    def read_run_results(self, run_name: str):
        results = self._DB.pull_run_results(run_name)
        if results:
            return [RunResult.from_json(result) for result in results]
        return list()

    # Returns a list of all Run Results contained in the database
    def read_all_run_results(self):
        find_all_results = self._DB.pull_all_run_results()
        if find_all_results:
            return [RunResult.from_json(result) for result in find_all_results]
        return list()

    def update_run_result(self, run_result: RunResult):
        run_result_json = RunResult.to_json(run_result)
        r = self._DB.update_run_result(run_result._run_configuration.get_run_name(),
                                   run_result.get_timestamp(), run_result_json)
        self.dataChanged.emit()

    def update_scan_result(self, run_name, run_result_timestamp, scan_result):
        scan_result_json = ScanResult.to_json(scan_result)
        self._DB.update_scan_result(run_name, run_result_timestamp, scan_result_json)

    # Currently non-functional
    '''
    def delete_run_Result(self):
        # TODO Implement this in DatabaseHandler
        self._DB.remove_run_Result()
        RunResultCRUD.notify_consumers()
    '''
