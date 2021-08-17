from abc import abstractmethod
from typing import Dict, Union, Tuple, Optional

from model import ToolConfiguration
from model import RunConfiguration

class AbstractController:
    def __init__(self):
        pass


class AbstractToolConfigurationCRUD(AbstractController):

    @abstractmethod
    def create_tool_configuration(self, tool_config: ToolConfiguration) -> Tuple[bool, Optional[str]]:
        pass

    @abstractmethod
    def read_tool_configuration(self, tool_id: str) -> Optional[ToolConfiguration]:
        pass

    @abstractmethod
    def update_tool_configuration(self, tool_id: str, tool_config: ToolConfiguration) -> bool:
        pass

    @abstractmethod
    def delete_tool_configuration(self, tool_id: str, *, return_config: bool = False) -> Union[bool, ToolConfiguration]:
        pass


class AbstractRunConfigurationCRUD(AbstractController):

    # TODO: Type hinting
    @abstractmethod
    def create_run_configuration(self, run_config: RunConfiguration):
        pass

    @abstractmethod
    def read_run_configuration(self, run_id: str):
        pass

    @abstractmethod
    def update_run_configuration(self):
        pass

    @abstractmethod
    def delete_run_configuration(self):
        pass
