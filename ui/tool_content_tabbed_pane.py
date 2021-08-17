from PyQt5 import QtWidgets
from functools import partial

from ui import ToolListWidget, ToolDependencyArea, ToolSpecificationArea


class ToolContentTabbedWidget(QtWidgets.QTabWidget):
    def __init__(self, parent: QtWidgets.QWidget = None):
        super().__init__(parent)

        tool_list_widget = ToolListWidget(self,
                                          add_function=partial(self.switch_view, 2))
        tool_dependency_area = ToolDependencyArea(self)
        tool_specification_area = ToolSpecificationArea(accept_function=partial(self.switch_view, 0),
                                                        cancel_function=partial(self.switch_view, 0))

        self.addTab(tool_list_widget, "Tool List")
        self.addTab(tool_dependency_area, "Tool Dependency")
        self.addTab(tool_specification_area, "Tool Specification")
        self.show()

    def switch_view(self, view: int):
        self.setCurrentIndex(view)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    r = ToolContentTabbedWidget()
    app.exec_()

