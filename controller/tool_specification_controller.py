from typing import Tuple, Optional, Union, List
from PyQt5.QtCore import QObject, pyqtSignal
from controller import AbstractToolConfigurationCRUD
from model import ToolConfiguration, DatabaseHandler


class Notifier(QObject):

    dataChanged: pyqtSignal = pyqtSignal()

    def __init__(self):
        if Notifier.__instance is not None:
            raise Exception('Only one instance of ToolConfigurationCRUD allowed.')
        else:
            super().__init__()
            self._DB: DatabaseHandler = DatabaseHandler.get_instance()

    # Contains the handle to the single instance
    __instance = None

    # Replaces the constructor as the method of obtaining an instance
    @staticmethod
    def get_instance():
        if Notifier.__instance is None:
            Notifier.__instance = Notifier()
            return Notifier.__instance
        else:
            return Notifier.__instance


class ToolConfigurationCRUD(AbstractToolConfigurationCRUD):
    DB = DatabaseHandler.get_instance()
    NOTIFIER = Notifier.get_instance()

    @staticmethod
    def create_tool_configuration(tool_config: ToolConfiguration) -> Tuple[bool, Optional[str]]:
        result = ToolConfigurationCRUD.DB.push_tool_configuration(tool_config.to_json())
        ToolConfigurationCRUD.NOTIFIER.dataChanged.emit()
        return result.acknowledged, result.inserted_id if result.acknowledged else None

    @staticmethod
    def read_tool_configuration(tool_id: str) -> Optional[ToolConfiguration]:
        find_one_result = ToolConfigurationCRUD.DB.pull_tool_configuration(tool_id)
        if find_one_result:
            return ToolConfiguration.from_json(find_one_result)

    @staticmethod
    def read_all_tool_configurations() -> Optional[List[ToolConfiguration]]:
        find_all_results = ToolConfigurationCRUD.DB.pull_all_tool_configurations()
        if find_all_results:
            return [ToolConfiguration.from_json(result) for result in find_all_results]

    @staticmethod
    def update_tool_configuration(tool_id: str, tool_config: ToolConfiguration) -> bool:
        ToolConfigurationCRUD.NOTIFIER.dataChanged.emit()
        return ToolConfigurationCRUD.DB.update_tool_configuration(tool_id, tool_config.to_json()).acknowledged

    @staticmethod
    def delete_tool_configuration(tool_id: str, *, return_config: bool = False) -> Union[bool, ToolConfiguration]:
        result = ToolConfigurationCRUD.DB.remove_tool_configuration(tool_id)
        ToolConfigurationCRUD.NOTIFIER.dataChanged.emit()
        if not result.acknowledged:
            return False
        return True if not return_config else ToolConfiguration.from_json(result.raw_result)
