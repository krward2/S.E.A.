from typing import List
from model.run_result import RunResult
from model import RunResult, AbstractSerializable


class XMLReport(AbstractSerializable):
    """
    Description: Contains a report in one run.
    
    Responsibilities:
    - (a) Knows name
    - (b) Knows description
    - (c) Knows at least one run result
    
    Collaborations:
    - (c) Run Result
    """

    @staticmethod
    def from_json(from_dict: dict) -> 'XMLReport':
        validated_keys = AbstractSerializable.validate_keys(["name", "description"], from_dict)
        if validated_keys:
            raise KeyError("The following keys must be specified: {}".format(", ".join(validated_keys)))

        xr = XMLReport(from_dict["name"], from_dict["description"])
        if "run_results" in from_dict:
            for run_result in from_dict["run_results"]:
                xr.add_run_result(RunResult.from_json(run_result))
        return xr

    def __init__(self, report_name: str, report_description: str,):
        #[SRS 32] table 10
        self._report_name: str = report_name
        self._report_description: str = report_description
            
        #[SRS 33]    
        self._run_results: List[RunResult] = list()

    def to_json(self) -> dict:
        return {
            "name": self._report_name,
            "description": self._report_description,
            "run_results": [rr.to_json() for rr in self._run_results]
        }
     
    #name
    def set_report_name(self, report_name: str) -> None:
        self._report_name = report_name
    
    def get_report_name(self) -> str:
        return self._report_name
    
    #description
    def set_report_description(self, report_description: str) -> None:
        self._report_description = report_description
    
    def get_report_description(self) -> str:
        return self._report_description
    
    #Run Result
    def get_run_results(self) -> List[RunResult]:
        return self._run_results
    
    def add_run_result(self, run_result: RunResult) -> bool:
        if run_result in self._run_results:
            return False
        self._run_results.append(run_result)
        return True
