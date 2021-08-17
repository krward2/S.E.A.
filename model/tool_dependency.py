from typing import Tuple, Optional

from model import DependentDataValue, AbstractSerializable


class DependencyExpression(AbstractSerializable):
    """
    Wrapper for [SRS 42] and [SRS 43] to improve Type Hinting
    """

    @staticmethod
    def from_json(from_dict: dict) -> 'DependencyExpression':
        if not AbstractSerializable.assert_present(from_dict, "operand1"):
            raise KeyError("operand1 must be specified")

        operator = from_dict.get("operator", None)
        operand2 = from_dict.get("operand2", None)

        if (operator is None) ^ (operand2 is None):
            raise ValueError("operator and operand2 must be specified if one is specified")

        return DependencyExpression(from_dict["operand1"], operator, operand2)

    def __init__(self, operand1: DependentDataValue, logical_operator: str = None, operand2: DependentDataValue = None):
        self._dependent_operands: Tuple[DependentDataValue, Optional[DependentDataValue]] = (operand1, operand2)
        self._logical_operator: Optional[str] = logical_operator

    def to_json(self) -> dict:
        return {
            "operand1": self._dependent_operands[0].to_json(),
            "operand2": self._dependent_operands[1].to_json(),
            "operator": self._logical_operator
        }


def create_dependency_expression(operand1: DependentDataValue, logical_operator: str = None, operand2: DependentDataValue = None) -> DependencyExpression:
    if logical_operator is None or operand2 is None:
        return DependencyExpression(operand1)
    else:
        return DependencyExpression(operand1=operand1, logical_operator=logical_operator, operand2=operand2)


class ToolDependency(AbstractSerializable):
    """
    Description: Contains the name of a dependency for a Tool
    
    Responsibilities:
    - (a) Knows name of Dependent Tool
    - (b) Knows Dependency Expression
    
    Collaborations:
    - (a) Tool Configuration
    - (b) Dependent Data Value

    This class is supported by the following SRS requirements:
        [SRS 41], [Table 14], [SRS 42], [SRS 43]
    """

    @staticmethod
    def from_json(from_dict: dict) -> 'ToolDependency':
        missing_keys = AbstractSerializable.validate_keys(["name", "dependency_expression"], from_dict)
        if missing_keys:
            raise KeyError("The following keys must be specified: {}".format(", ".join(missing_keys)))

        return ToolDependency(from_dict["name"], DependencyExpression.from_json(from_dict["dependency_expression"]))

    def __init__(self, tool_name: str, dependency_expression: DependencyExpression):
        self._tool_name: str = tool_name
        self._dependency_expression: DependencyExpression = dependency_expression

    def to_json(self) -> dict:
        return {
            "name": self._tool_name,
            "dependency_expression": self._dependency_expression.to_json()
        }
