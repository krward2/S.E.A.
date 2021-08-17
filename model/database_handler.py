from enum import Enum
from typing import List, Union

from bson import ObjectId
from pymongo import MongoClient
from pymongo.results import UpdateResult, DeleteResult


class DatabaseHandler:
    """
    Description: A wrapper class for the underlying database application. Ensures a smooth and consistent communication layer exists between our system and the database application
    
    Responsibilities:
    - (a) Push data to database
    - (b) Pull data from database
    - (c) Query database to check for the existence of fields and values
    
    Collaborations:
    """

    class Collections(Enum):
        RUN = "run"
        RUN_RESULT = "run_result"
        SCAN = "scan"
        CONFIG = "config"

    __instance = None

    @staticmethod
    def get_instance():
        if DatabaseHandler.__instance == None:
            DatabaseHandler()
        return DatabaseHandler.__instance

    def __init__(self):
        if DatabaseHandler.__instance != None:
            raise Exception('Only one instance of DatabaseHandler allowed')
        else:
            DatabaseHandler.__instance = self
            self.__client = MongoClient("mongodb://localhost:27017")
            self.__db = self.__client["db"]

    def push_scan_configuration(self, scan_configuration: dict):
        """Pushes a scan configuration to the Database

        :param scan_configuration: The dictionary of a scan configuration to push
        """
        self.__db[DatabaseHandler.Collections.SCAN.value].insert_one(scan_configuration)

    def pull_scan_configuration(self, scan_name: str) -> Union[dict, None]:
        """Returns the scan configuration that matches the name given

        Note that if a configuration is not found with the specified name,
        None will be returned.

        :param scan_name: The scan name to search for a configuration for
        """
        return self.__db[DatabaseHandler.Collections.SCAN.value].find_one({"scan_name": scan_name})

    def push_run_configuration(self, run_configuration: dict):
        """Pushes a run configuration to the Database

        :param run_configuration: The dictionary of a run configuration to push
        """
        return self.__db[DatabaseHandler.Collections.RUN.value].insert_one(run_configuration)

    def pull_run_configuration(self, run_name: str):
        """Returns the run configuration that matches the name given

        Note that if a configuration is not found with the specified name,
        None will be returned.

        :param run_name: The run name to search for a configuration for
        """
        return self.__db[DatabaseHandler.Collections.RUN.value].find_one({"name": run_name})

    def pull_all_run_configurations(self):
        return list(self.__db[DatabaseHandler.Collections.RUN.value].find({}))

    def update_run_configuration(self, run_id: str, run_configuration: dict) -> UpdateResult:
        """Updates the run that has the specified ID with the specified run configuration
        JSON object

        :param run_id: The ID of the run to update
        :param run_configuration: The JSON object of the run configuration to use to update in the database
        """
        return self.__db[DatabaseHandler.Collections.RUN.value].update_one({"name": run_id}, {"$set": run_configuration})

    def push_tool_configuration(self, tool_configuration: dict):
        """Pushes a tool configuration to the Database

        :param tool_configuration: The dictionary of a tool configuration to push
        """
        return self.__db[DatabaseHandler.Collections.CONFIG.value].insert_one(tool_configuration)

    def pull_tool_configuration(self, tool_id: str) -> Union[dict, None]:
        """Returns the tool configuration that matches the name given

        Note that if a configuration is not found with the specified name,
        None will be returned.

        :param tool_id: The ID of the search for a configuration for
        """
        return self.__db[DatabaseHandler.Collections.CONFIG.value].find_one({"_id": tool_id})

    def update_tool_configuration(self, tool_id: str, tool_configuration: dict) -> UpdateResult:
        """Updates the tool that has the specified ID with the specified tool configuration
        JSON object

        :param tool_id: The ID of the tool to update
        :param tool_configuration: The JSON object of the tool configuration to use to update in the database
        """
        return self.__db[DatabaseHandler.Collections.CONFIG.value].update_one({"_id": tool_id}, {"$set": tool_configuration})

    def remove_tool_configuration(self, tool_id: str) -> DeleteResult:
        """Removes the specified tool configuration based off the
        tool id

        :param tool_id: The ID of the tool to remove
        """
        return self.__db[DatabaseHandler.Collections.CONFIG.value].delete_one({"_id": ObjectId(tool_id)})

    def pull_all_tool_configurations(self) -> List[dict]:
        """Returns a list of all tool configurations
        """
        return list(self.__db[DatabaseHandler.Collections.CONFIG.value].find())

    def push_run_result(self, run_result: dict):
        """Pushes a run result to the Database

        :param run_result: The dictionary of a run result to push
        """
        return self.__db[DatabaseHandler.Collections.RUN_RESULT.value].insert_one(run_result)

    def pull_run_result(self, run_name: str, timestamp: str):
        """Returns the run result that matches the name given

        Note that if a result is not found with the specified run name,
        None will be returned.

        :param run_name: The run name associated with the run result to search for
        :param timestamp: The timestamp associated with the run result
        """
        return self.__db[DatabaseHandler.Collections.RUN_RESULT.value].find_one({"run_configuration.name": run_name, "timestamp": timestamp})

    def pull_run_results(self, run_name: str):
        """Returns the run results that matches the run name given

        Note that if results are not found with the specified run name,
        None will be returned.

        :param run_name: The run name associated with the run results to search for
        """
        return list(self.__db[DatabaseHandler.Collections.RUN_RESULT.value].find({"run_configuration.name": run_name}))

    def pull_all_run_results(self):
        return list(self.__db[DatabaseHandler.Collections.RUN_RESULT.value].find({}))

    def update_run_result(self, run_name: str, run_result_timestamp: str, run_result: dict) -> UpdateResult:
        """Updates the run that has the specified ID with the specified run configuration
        JSON object

        :param run_name: The name of the run associated with the run result to update
        :param run_result_timestamp: The timestamp associated with the run result to be updated
        :param run_result: The JSON object of the run result to use to update in the database
        """
        return self.__db[DatabaseHandler.Collections.RUN_RESULT.value].\
            replace_one({"run_configuration.name": run_name, "timestamp": run_result_timestamp}, run_result)


if __name__ == "__main__":
    d = DatabaseHandler.get_instance()
    d.push_tool_configuration({
        "tool_name": "nmap",
        "tool_description": "Network Mapping",
        "tool_path": "/usr/bin/nmap"
    })
    print(d.pull_all_tool_configurations())
