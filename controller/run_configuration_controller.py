from PyQt5.QtCore import QObject, pyqtSignal

from controller import AbstractRunConfigurationCRUD
from model import RunConfiguration, DatabaseHandler


class RunConfigurationCRUD(QObject):
    """
        A Singleton controller class responsible for CRUD operations on the Run Configuration collection,
        and for notifying relevant UI widgets of changes to data.
        """

    dataChanged: pyqtSignal = pyqtSignal()

    def __init__(self):
        super().__init__()
        if RunConfigurationCRUD.__instance is not None:
            raise Exception('Only one instance of RunConfigurationCRUD allowed.')
        else:
            self._DB: DatabaseHandler = DatabaseHandler.get_instance()

    # Contains the handle to the single instance
    __instance = None

    # Replaces the constructor as the method of obtaining an instance
    @staticmethod
    def get_instance():
        if RunConfigurationCRUD.__instance is None:
            RunConfigurationCRUD.__instance = RunConfigurationCRUD()
            return RunConfigurationCRUD.__instance
        else:
            return RunConfigurationCRUD.__instance

    # Adds a new Run Configuration to the database
    def create_run_configuration(self, run_config: RunConfiguration):
        result = self._DB.push_run_configuration(run_config.to_json())
        self.dataChanged.emit()
        return result.acknowledged, result.inserted_id if result.acknowledged else None

    # Returns the Run Configuration associated the given run_id
    def read_run_configuration(self, run_name: str):
        result = self._DB.pull_run_configuration(run_name)
        if result:
            return result

    # Returns a list of all Run Configurations contained in the database
    def read_all_run_configurations(self):
        find_all_results = self._DB.pull_all_run_configurations()
        if find_all_results:
            return [RunConfiguration.from_json(result) for result in find_all_results]
        else:
            return list()
    # Currently non-functional
    def update_run_configuration(self, run_config: RunConfiguration):
        # TODO Implement update_run_configuration in DatabaseHandler
        run_config_json = RunConfiguration.to_json(run_config)
        self._DB.update_run_configuration(run_config.get_run_name(), run_config_json)
        self.dataChanged.emit()

    # Currently non-functional
    def delete_run_configuration(self):
        # TODO Implement this in DatabaseHandler
        self._DB.remove_run_configuration()
        self.dataChanged.emit()
