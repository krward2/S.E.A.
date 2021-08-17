from model import AbstractSerializable


class OutputDataSpecification:
    """
    Description: Contains information about the output of a Tool
    
    Responsibilities:
    - (a) Knows data element
    - (b) Knows data type
    
    Collaborations:

    This class is supported by the following SRS requirements:
        [SRS 30], [Table 13]
    """

    @staticmethod
    def from_json(from_dict: dict) -> 'OutputDataSpecification':
        if not AbstractSerializable.assert_present(from_dict, "element", "type"):
            raise KeyError("element and type keys must be specified")

        return OutputDataSpecification(from_dict["element"], from_dict["type"])

    def __init__(self, data_element: str, data_type: str):
        # Explicit Attributes Based on Table 13
        self._data_element: str = data_element
        self._data_type: str = data_type

    def to_json(self) -> dict:
        return {
            "element": self._data_element,
            "type": self._data_type
        }
        
    # Editable Attributes Based on Table 11

    def set_data_element(self, data_element: str) -> None:
        self._data_element = data_element

    def get_data_element(self) -> str:
        return self._data_element
    
    def set_data_type(self, data_type: str) -> None:
        self._data_type = data_type
    
    def get_data_type(self) -> str:
        return self._data_type
