
from enum import Enum

class RunState(Enum):
    UNCONFIGURED = "Unconfigured"
    CONFIGURED = "Configured"
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    TERMINATED = "Terminated"

class ScanState(Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    PAUSED = "Paused"
    TERMINATED = "Terminated"