from typing import Optional, List

from model import AbstractSerializable


class ToolOptionArgument(AbstractSerializable):
    """
    Description: Contains options and arguments that will be passed to the appropriate Underlying Tool
    
    Responsibilities:
    - (a) Knows Tool Options
    - (b) Knows Tool Arguments
    
    Collaborations:
    """

    @staticmethod
    def from_json(from_dict: dict) -> 'ToolOptionArgument':
        missing_keys = AbstractSerializable.validate_keys(["option"], from_dict)
        if missing_keys:
            raise KeyError("The following keys must be specified: {}".format(", ".join(missing_keys)))

        argument = from_dict.get("argument", "")
        return ToolOptionArgument(from_dict["option"], argument)

    def __init__(self, option: str, argument: Optional[str] = ""):
        self.__option = option
        self.__argument = argument

    def to_json(self) -> dict:
        return {
            "option": self.__option,
            "argument": self.__argument
        }

    def to_list(self) -> List[str]:
        arg_list = [self.__option, self.__argument]
        while '' in arg_list:
            arg_list.remove('')
        return arg_list

    def get_option(self):
        return self.__option

    def get_argument(self):
        return self.__argument

    def set_option(self, option: str):
        self.__option = option

    def set_argument(self, argument: str):
        self.__argument = argument
