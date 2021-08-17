from typing import List, Optional
from model import AbstractSerializable, ToolOptionArgument, OutputDataSpecification, ToolDependency, DatabaseHandler


class ToolConfiguration(AbstractSerializable):
    """
    Description: The configuration for a Tool inside the SEA system
    
    Responsibilities:
    - (a) Knows name
    - (b) Knows description
    - (c) Knows path
    - (d) Knows at least one tool option argument
    - (e) Knows at least one output data specification
    - (f) Knows at most one tool dependency
    
    Collaborations:
    - (d) Tool Option Argument
    - (e) Output Data Specification
    - (f) Tool Dependency

    This class is supported by the following SRS requirements:
        [SRS 35], [Table 11], [SRS 36], [SRS 37], [SRS 38]
    """

    @staticmethod
    def from_json(from_dict: dict) -> 'ToolConfiguration':
        missing_keys = AbstractSerializable.validate_keys(["name", "description", "path"], from_dict)
        if missing_keys:
            raise KeyError("The following keys must be specified: {}".format(", ".join(missing_keys)))

        tc = ToolConfiguration(from_dict["name"], from_dict["description"], from_dict["path"])

        # This loads all Tool Option Arguments from the dictionary
        toas = [
            ToolOptionArgument.from_json(toa)
            for toa in from_dict["option_arguments"]
        ]
        for toa in toas:
            tc.add_tool_option_argument(toa)

        # This loads all Output Data Specifications from the dictionary
        odss = [
            OutputDataSpecification.from_json(ods)
            for ods in from_dict["output_data_specifications"]
        ]
        for ods in odss:
            tc.add_output_data_specifications(ods)

        # dependency = ToolDependency.from_json(from_dict["dependency"])
        # tc.set_tool_dependency(dependency)
        return tc

    def __init__(self, tool_name: str, tool_description: str, tool_path: str):
        # Explicit Attributes Based on Table 11
        self._tool_name: str = tool_name
        self._tool_description: str = tool_description
        self._tool_path: str = tool_path
        # Implied Attributes Based on [SRS 36 - 38]
        self._tool_option_arguments: List[ToolOptionArgument] = list()
        self._output_data_specifications: List[OutputDataSpecification] = list()
        self._tool_dependency: Optional[ToolDependency] = None

    def to_json(self):
        return {
            "name": self._tool_name,
            "description": self._tool_description,
            "path": self._tool_path,
            "option_arguments": [toa.to_json() for toa in self._tool_option_arguments],
            "output_data_specifications": [ods.to_json() for ods in self._output_data_specifications],
            # "dependency": self._tool_dependency.to_json() if self._tool_dependency else None
        }

    # Editable Attributes Based on Table 11

    def set_tool_name(self, tool_name: str) -> None:
        self._tool_name = tool_name

    def get_tool_name(self) -> str:
        return self._tool_name

    def set_tool_description(self, tool_description: str) -> None:
        self._tool_description = tool_description

    def get_tool_description(self) -> str:
        return self._tool_description

    def set_tool_path(self, tool_path: str) -> None:
        self._tool_path = tool_path

    def get_tool_path(self) -> str:
        return self._tool_path

    # Editable Attributes Based on [SRS 36]

    def get_tool_option_arguments(self) -> List[ToolOptionArgument]:
        return self._tool_option_arguments

    def add_tool_option_argument(self, tool_option_argument: ToolOptionArgument) -> bool:
        """
        Attempts to add a new Tool Option Argument to this Tool Configuration
        \returns True if the tool option argument was not already part of this tool configuration and was added
        """
        if tool_option_argument in self._tool_option_arguments:
            return False
        self._tool_option_arguments.append(tool_option_argument)
        return True

    def remove_tool_option_argument(self, tool_option_argument: ToolOptionArgument) -> bool:
        """
        Attempts to remove a Tool Option Argument from this Tool Configuration
        \returns True if the tool option argument was part of this tool configuration and was removed
        """
        if tool_option_argument not in self._tool_option_arguments:
            return False
        self._tool_option_arguments.remove(tool_option_argument)
        return True

    # Editable Attributes Based on [SRS 37]

    def get_output_data_specifications(self) -> List[OutputDataSpecification]:
        return self._tool_option_arguments

    def add_output_data_specifications(self, output_data_specifications: OutputDataSpecification) -> bool:
        """
        Attempts to add a new Tool Option Argument to this Tool Configuration
        \returns True if the tool option argument was not already part of this tool configuration and was added
        """
        if output_data_specifications in self._output_data_specifications:
            return False
        self._output_data_specifications.append(output_data_specifications)
        return True

    def remove_output_data_specifications(self, output_data_specifications: OutputDataSpecification) -> bool:
        """
        Attempts to remove a Tool Option Argument from this Tool Configuration
        \returns True if the tool option argument was part of this tool configuration and was removed
        """
        if output_data_specifications not in self._output_data_specifications:
            return False
        self._output_data_specifications.remove(output_data_specifications)
        return True

    # Editable Attributes Based on [SRS 38]

    def set_tool_dependency(self, tool_dependency: ToolDependency) -> None:
        self._tool_dependency = tool_dependency

    def get_tool_dependency(self) -> ToolDependency:
        return self._tool_dependency

    def push_to_database(self) -> None:
        tool_config_dict = {'tool_name': self._tool_name, 'tool_description': self._tool_description,
                            'tool_path': self._tool_path, 'option_args': self._tool_option_arguments,
                            'output_data_specifications': self._output_data_specifications}

        DatabaseHandler.get_instance().push_tool_configuration(tool_config_dict)

    def get_arg_list(self) -> List[str]:
        arg_list = list()
        for arg in self._tool_option_arguments:
            arg_list += arg.to_list()
        return arg_list
