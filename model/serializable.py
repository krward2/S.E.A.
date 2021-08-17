import warnings
from abc import abstractmethod
from typing import List, Any, Iterable


class AbstractSerializable:

    @abstractmethod
    def to_json(self) -> dict:
        pass

    @staticmethod
    @abstractmethod
    def from_json(from_dict: dict) -> 'AbstractSerializable':
        pass

    @staticmethod
    def assert_present(dictionary: dict, *strs: str) -> bool:
        warnings.warn("assert_present is deprecated. Use validate_keys instead", DeprecationWarning)
        return {*strs}.issubset(set(dictionary.keys()))
    
    @staticmethod
    def validate_keys(keys: Iterable[Any], collection: Iterable[Any]) -> List[Any]:
        """
            Validates that all provided keys are present in the given collection

            :param keys: The list of keys that must be present
            :param collection: The collection to check for the keys in

            :returns: A list containing all keys that were not present
        """
        return [key for key in keys if key not in collection]

