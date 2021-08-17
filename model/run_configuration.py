from typing import List

from model import Target, ScanConfiguration, RunState, AbstractSerializable

class RunConfiguration(AbstractSerializable):
    """
    Description: A container class containing all of the crucial information for defining a Run.
    This configuration may be saved to both the database and to disk, as well as loaded from disk.
    
    Responsibilities:
    - (a) Knows Target
    - (b) Knows at least one Scan Configuration
    - (c) Knows Name
    - (d) Knows Description
    - (e) Knows State
    - (f) Saves own configuration to the database
    
    Collaborations:
    - (a) Target
    - (b) Scan Configuration
    - (f) Database Handler

    This class is supported by the following SRS requirements:
        [SRS 21], [SRS 22], [SRS 23], [Table 5]
    """

    def __init__(self, target: Target, run_name: str, run_description: str, state=None):
        # [SRS 21]
        self._target: Target = target
        # [SRS 22]
        self._scan_configurations: List[ScanConfiguration] = list()
        # [SRS 23] -> [Table 5]
        self._run_name: str = run_name
        self._run_description: str = run_description
        self._run_state: str = RunState.CONFIGURED.value if not state else state

    def set_run_name(self, run_name: str) -> None:
        self._run_name = run_name

    def get_run_name(self) -> str:
        return self._run_name

    def set_run_description(self, run_description: str) -> None:
        self._run_description = run_description

    def get_run_description(self) -> str:
        return self._run_description

    def set_run_state(self, run_state) -> None:
        self._run_state = run_state

    def get_run_state(self):
        return self._run_state

    def get_target(self) -> Target:
        return self._target

    def set_target(self, target: Target) -> None:
        self._target = target

    def get_scan_configurations(self) -> List[ScanConfiguration]:
        return self._scan_configurations

    def add_scan_configuration(self, scan_configuration: ScanConfiguration) -> bool:
        if scan_configuration in self._scan_configurations:
            return False
        self._scan_configurations.append(scan_configuration)
        return True

    def remove_scan_configuration(self, scan_configuration: ScanConfiguration) -> bool:
        if scan_configuration not in self._scan_configurations:
            return False
        self._scan_configurations.remove(scan_configuration)
        return True

    # JSON serialization
    def to_json(self) -> dict:
        return {
            "target": self._target.to_json(),
            "scan_configurations": [config.to_json() for config in self._scan_configurations],
            "name": self._run_name,
            "description": self._run_description,
            "run_state": self._run_state
        }

    @staticmethod
    def from_json(json_dict: dict) -> 'RunConfiguration':

        # Check for critical information
        validated_keys = AbstractSerializable.validate_keys(["target", "name"], json_dict)
        if validated_keys:
            raise KeyError("RunConfiguration is missing key(s): %s" % validated_keys)
        # Extract information
        target = Target.from_json(json_dict.get("target"))
        name = json_dict.get("name")
        description = json_dict.get("description", None)
        state = json_dict.get("run_state")
        scan_configurations = [ScanConfiguration.from_json(config) for config in
                               json_dict.get("scan_configurations", list())]
        # Generate RunConfiguration instance
        rc = RunConfiguration(target, name, description, state)
        for sc in scan_configurations:
            rc.add_scan_configuration(sc)
        return rc


if __name__ == '__main__':
    from model import RunState
    from model import Target

    #TODO re-add AbstractSerializable
    t = Target()
    r = RunState
    rc = RunConfiguration(t, 'Run 1', 'A Run', r)

    print(rc)