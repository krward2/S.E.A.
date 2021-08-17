from model import AbstractSerializable, ScanState, ToolConfiguration


class ScanConfiguration(AbstractSerializable):
    """
    Description: Contains all the information for a scan. This will save the result to the database, which includes the output and setting of the scan.
    
    Responsibilities:
    - (a) Knows name
    - (b) Knows execution number
    - (c) Knows state
    - (d) Save Scan Results to database
    
    Collaborations:
    - (a) Tool Configuration
    - (d) Scan Results, Database Handler

    This class addressed SRS[25] and SRS[26]
    """

    @staticmethod
    def from_json(from_dict: dict) -> 'ScanConfiguration':
        missing_keys = AbstractSerializable.validate_keys(["name", "tool_configuration"], from_dict)
        if missing_keys:
            raise KeyError("The following keys must be specified: {}".format(", ".join(missing_keys)))

        return ScanConfiguration(from_dict["name"], ToolConfiguration.from_json(from_dict["tool_configuration"]))

    def __init__(self, scan_name: str, tool_configuration: ToolConfiguration):
        # SRS[25]
        self._scan_name: str = scan_name
        self._execution_number: int = -1
        self._scan_state: ScanState = ScanState.INACTIVE.value
        # SRS[26]
        self._tool_configuration: ToolConfiguration = tool_configuration

    def to_json(self) -> dict:
        return {
            "name": self._scan_name,
            "tool_configuration": self._tool_configuration.to_json()
        }

    def get_scan_name(self) -> str:
        return self._scan_name

    def set_scan_name(self, scan_name: str):
        self._scan_name = scan_name

    def get_tool_configuration(self):
        return self._tool_configuration

    def set_scan_state(self, state: ScanState):
        self._scan_state = state

    def get_scan_state(self):
        return self._scan_state

    def get_execution_number(self):
        return self._execution_number

    def set_scan_state(self, state: ScanState):
        self._scan_state = state

    def get_scan_state(self):
        return self._scan_state

    def get_execution_number(self):
        return self._execution_number