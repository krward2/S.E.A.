from typing import List, Union

from model import ScanConfiguration, AbstractSerializable


class ScanResult(AbstractSerializable):
    """
    Description: Contains information related to the execution of a Scan.
    
    Responsibilities:
    - (a) Knows Scan Start/End Time
    - (b) Knows Scanned IP’d
    - (c) Knows Execution Status
    - (d) Knows formatted Scan Output
    
    Collaborations:

    This class is supported by the following SRS requirements:
        [SRS 27], [Table 8], [SRS 28]
    """

    STATUS_SUCCESS = True
    STATUS_FAILURE = False

    @staticmethod
    def from_json(from_dict: dict) -> 'ScanResult':
        missing_keys = AbstractSerializable.validate_keys(["scan_configuration", "start_time", "end_time", "scanned_ips"], from_dict)
        if missing_keys:
            raise KeyError("The following keys must be specified: {}".format(", ".join(missing_keys)))

        sr = ScanResult(ScanConfiguration.from_json(from_dict["scan_configuration"]))
        sr.set_scan_start_time(from_dict["start_time"])
        sr.set_scan_end_time(from_dict["end_time"])
        sr.set_scanned_ips(from_dict["scanned_ips"])
        sr.set_formatted_scan_output(from_dict["formatted_scan_output"])
        return sr

    def __init__(self, scan_configuration: ScanConfiguration):
        # [SRS 27] -> [Table 8]
        self._scan_start_time: Union[str, None] = None  # Not optional but not known at start
        self._scan_end_time: Union[str, None] = None  # Not optional but not known at start
        self._scanned_ips: List[str] = list()  # Not optional but not known at start
        self._execution_status: bool = ScanResult.STATUS_SUCCESS  # Not optional but not known at start
        self._formatted_scan_output: str = ''  # Not optional but not known at
        # [SRS 28]
        self._scan_configuration: ScanConfiguration = scan_configuration

    def to_json(self) -> dict:
        return {
            "scan_configuration": self._scan_configuration.to_json(),
            "start_time": self._scan_start_time,
            "end_time": self._scan_end_time,
            "scanned_ips": list(self._scanned_ips),
            "formatted_scan_output": self._formatted_scan_output
        }
    
    def get_scan_start_time(self) -> str:
        return self._scan_start_time
    
    def get_scan_end_time(self) -> str:
        return self._scan_end_time
    
    def get_scanned_ips(self) -> List[str]:
        return self._scanned_ips
    
    def get_execution_status(self) -> bool:
        return self._execution_status

    def set_formatted_scan_output(self, output: str):
        self._formatted_scan_output = output

    def get_formatted_scan_output(self) -> str:
        return self._formatted_scan_output

    def set_scan_start_time(self, scan_start_time: str):
        self._scan_start_time = scan_start_time

    def set_scan_end_time(self, scan_end_time: str):
        self._scan_end_time = scan_end_time

    def set_scanned_ips(self, scanned_ips: List[str]):
        self._scanned_ips = scanned_ips

    def get_scan_name(self):
        return self._scan_configuration.get_scan_name()

    def get_scan_configuration(self):
        return self._scan_configuration