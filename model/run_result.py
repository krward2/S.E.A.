from typing import List, Dict
from model import RunConfiguration, ScanResult, AbstractSerializable


class RunResult(AbstractSerializable):
    """
    Description: Contains information about results for a Run

    Responsibilities:
    - (a) Knows timestamp
    - (b) Knows at least one scan result
    - (c) Knows run configuration
    
    Collaborations:
    - (b) Scan Result
    - (c) Run Configuration
    """
    def __init__(self, timestamp: str, run_configuration: RunConfiguration):
        #[SRS 29] table 9
        self._timestamp: str = timestamp
        #[SRS 30]
        self._scan_results: List[ScanResult] = list()
        #[SRS 31]    
        self._run_configuration: RunConfiguration = run_configuration
     
    #timestamp
    def get_timestamp(self):
        return self._timestamp

    def set_timestamp(self, timestamp: str):
        self._timestamp = timestamp
        
    def get_scan_results(self) -> List[ScanResult]:
        return self._scan_results
    
    def add_scan_result(self, scan_result: ScanResult) -> bool:
        if scan_result in self._scan_results:
            return False
        self._scan_results.append(scan_result)
        return True
    
    def remove_scan_result(self, scan_result: ScanResult) -> bool:
        if scan_result not in self._scan_results:
            return False
        self._scan_results.remove(scan_result)
        return True
    
    #Run Configuration
    def get_run_configuration(self) -> List[RunConfiguration]:
        return self._run_configuration
        
    def add_run_configuration(self, run_configuration: RunConfiguration) -> bool:
        self._run_configuration = run_configuration
        return True

    def add_scan_result(self, scan_result):
        self._scan_results.append(scan_result)

    # JSON Serialization
    def to_json(self) -> Dict:
        return {
            "timestamp": self._timestamp,
            "scan_result": [result.to_json() for result in self._scan_results],
            "run_configuration": self._run_configuration.to_json()
        }
    
    @staticmethod
    def from_json(json_dict: Dict) -> 'RunResult':
        # Check for keys
        missing_keys = AbstractSerializable.validate_keys(["timestamp", "scan_result", "run_configuration"], json_dict)
        if missing_keys:
            raise KeyError("RunResult is missing the following keys: %s" % str(missing_keys))
        # Extract Information
        #timestamp = datetime.fromtimestamp(json_dict.get("timestamp"))
        timestamp = json_dict.get("timestamp")
        scan_results = [ScanResult.from_json(srt) for srt in json_dict.get("scan_result")]
        rc = RunConfiguration.from_json(json_dict.get("run_configuration"))
        # Create the instance
        rr = RunResult(timestamp, rc)
        for sr in scan_results:
            print('adding scan result')
            rr.add_scan_result(sr)
        return rr
        