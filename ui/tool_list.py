from functools import partial

from PyQt5 import QtWidgets, QtCore

from model import DatabaseHandler
from controller.tool_specification_controller import Notifier

DB = DatabaseHandler.get_instance()


class ToolListTable(QtWidgets.QTableWidget):

    def __init__(self, parent: QtWidgets.QWidget = None):
        super().__init__(parent)
        Notifier.get_instance().dataChanged.connect(self.update_data)

        self.tool_list = [
            {
                "id": tool["_id"],
                "name": tool["name"],
                "desc": tool["description"],
                "path": tool["path"]
            }
            for tool in DB.pull_all_tool_configurations()
        ]
        self.reverse = False

        self.setColumnCount(3)
        self.setHorizontalHeaderLabels(list(["Name", "Description", ""]))
        self.horizontalHeader().sectionClicked.connect(self.sort_tools)

        self.sort_tools()

        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

    def sort_tools(self):
        self.reverse = not self.reverse
        self.update_data()

    def update_data(self):
        for i in range(len(self.tool_list)):
            self.removeRow(0)
        self.clear()
        self.tool_list = [
            {
                "id": tool["_id"],
                "name": tool["name"],
                "desc": tool["description"],
                "path": tool["path"]
            }
            for tool in DB.pull_all_tool_configurations()
        ]
        self.tool_list.sort(key=lambda d: d["name"], reverse=self.reverse)
        self.setHorizontalHeaderLabels(["Name", "Description", ""])
        for i in range(len(self.tool_list)):
            self.insertRow(i)
            name_label = QtWidgets.QLabel(self.tool_list[i]["name"], self)
            desc_label = QtWidgets.QLabel(self.tool_list[i]["desc"], self)
            remove_button = QtWidgets.QPushButton("Remove", self)
            remove_button.clicked.connect(partial(self.remove_tool, i))
            self.setCellWidget(i, 0, name_label)
            self.setCellWidget(i, 1, desc_label)
            self.setCellWidget(i, 2, remove_button)

    def remove_tool(self, index: int):
        self.removeRow(index)
        tool = self.tool_list[index]
        DB.remove_tool_configuration(tool["id"])


class ToolListWidget(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget = None, flags=QtCore.Qt.WindowFlags(),
                 *, add_function: callable = None):
        super().__init__(parent, flags)

        layout = QtWidgets.QVBoxLayout()

        tool_list_label = QtWidgets.QLabel("Tool List", self)
        add_button = QtWidgets.QPushButton("Add", self)
        if add_function:
            add_button.clicked.connect(add_function)
        tool_list_table = ToolListTable()
        tool_list_table.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                      QtWidgets.QSizePolicy.Expanding)

        layout.addWidget(tool_list_label)
        layout.addWidget(tool_list_table)
        layout.addWidget(add_button)

        self.setLayout(layout)
