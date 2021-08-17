from enum import Enum
from typing import Union
from model import AbstractSerializable


class DependentDataValue(AbstractSerializable):
    """
    Description: Defines the criterion for determining which IP addresses should be used as input of a Scan
    
    Responsibilities:
    - (a) Knows dependent criterion
    - (b) Knows relational operator
    - (c) Knows dependent criterion value
    
    Collaborations:
    """

    class Operator(Enum):
        LT = "<"
        GT = ">"
        LE = "<="
        GE = ">="
        E = "=="
        NE = "~="

        def __str__(self):
            return self.value
        
        def __repr__(self):
            return self.value

    def __init__(self, criterion: str, operator: Union[Operator, str], criterion_value: str):
        self.__criterion: str = criterion
        if isinstance(operator, DependentDataValue.Operator):
            operator = str(operator)
        self.__operator: str = operator
        self.__criterion_value: str = criterion_value

    def get_criterion(self) -> str:
        return self.__criterion

    def get_operator(self) -> str:
        return self.__operator

    def get_value(self) -> str:
        return self.__criterion_value

    def to_json(self) -> dict:
        return {
            "criterion": self.get_criterion(),
            "operator": self.get_operator(),
            "value": self.get_value()
        }
    
    @staticmethod
    def from_json(json_dict: dict) -> 'DependentDataValue':
        validated_keys = AbstractSerializable.validate_keys(["criterion", "operator", "value"], json_dict)
        if len(validated_keys) != 0:
            raise KeyError("The following keys must be specified: {}".format(", ".join(validated_keys)))

        criterion = json_dict.get("criterion")
        operator = json_dict.get("operator")
        value = json_dict.get("value")
        return DependentDataValue(criterion=criterion, operator=operator, criterion_value=value)
