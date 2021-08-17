from typing import List
from model import AbstractSerializable


class MutualExclusivityError(Exception):
    def __init__(self, msg='Whitelist and Blacklist are not mutually exclusive'):
        super().__init__(msg)


class DuplicateIPError(Exception):
    def __init__(self, msg='Duplicate IPs'):
        super().__init__(msg)


class IPRemovalError(Exception):
    def __init__(self, msg='Cannot remove IP. No such IP.'):
        super().__init__(msg)


class Target(AbstractSerializable):
    """
    Description: Contains a list of IP’s that can and cannot be scanned during a Run
    
    Responsibilities:
    - Knows Whitelist IP’s
    - Knows Blacklist IP’s
    
    Collaborations:

    This class is supported by the following SRS requirements:
        [SRS 24], [Table 6]

    TODO: Ensure mutual exclusivity between the whitelist and blacklist.
    """

    def __init__(self):
        self._whitelist: List[str] = list()
        self._blacklist: List[str] = list()

    # Whitelist

    def add_to_whitelist(self, ip_address: str):
        if ip_address in self._whitelist:
            raise DuplicateIPError()
        if ip_address in self._blacklist:
            raise MutualExclusivityError()
        self._whitelist.append(ip_address)

    def remove_from_whitelist(self, ip_address: str):
        if ip_address not in self._whitelist:
            raise IPRemovalError()
        self._whitelist.remove(ip_address)

    def get_whitelist(self) -> List[str]:
        return self._whitelist

    # Blackist

    def add_to_blacklist(self, ip_address: str):
        if ip_address in self._blacklist:
            raise DuplicateIPError()
        if ip_address in self._whitelist:
            raise MutualExclusivityError()
        self._blacklist.append(ip_address)

    def remove_from_blacklist(self, ip_address: str):
        if ip_address not in self._blacklist:
            raise IPRemovalError()
        self._blacklist.remove(ip_address)

    def get_blacklist(self) -> List[str]:
        return self._blacklist

    # JSON Serialization

    def to_json(self) -> dict:
        return {
            "whitelist": [s for s in self._whitelist],
            "blacklist": [s for s in self._blacklist]
        }

    @staticmethod
    def from_json(json_dict: dict) -> 'Target':
        # Check for keys
        missing_keys = AbstractSerializable.validate_keys(["whitelist", "blacklist"], json_dict)
        if missing_keys:
            raise KeyError("Target is missing the following key(s): %s" % str(missing_keys))
        # Extract information
        whitelist = json_dict.get("whitelist")
        blacklist = json_dict.get("blacklist")
        # Create instance
        target = Target()
        for ip in whitelist:
            target.add_to_whitelist(ip)
        for ip in blacklist:
            target.add_to_blacklist(ip)
        return target
