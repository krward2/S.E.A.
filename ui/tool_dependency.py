import sys

from PyQt5 import QtWidgets, QtCore

from ui.util import add_grid_to_layout


class ToolDependencyArea(QtWidgets.QWidget):
    """
    Author: Jonah Pierce

    Covers: [SRS 18]
    """

    def __init__(self, parent: QtWidgets.QWidget = None, flags=QtCore.Qt.WindowFlags()):
        super().__init__(parent, flags)

        layout = QtWidgets.QGridLayout()

        self.scroll_area = RemovableDependencyScrollArea(self)

        save_button = QtWidgets.QPushButton("Save", self)
        cancel_button = QtWidgets.QPushButton("Cancel", self)

        layout.addWidget(self.scroll_area, 0, 0, 1, 2)
        layout.addWidget(save_button, 1, 0)
        layout.addWidget(cancel_button, 1, 1)

        self.setLayout(layout)
        self.show()


class RemovableDependencyScrollArea(QtWidgets.QScrollArea):
    def __init__(self, parent: QtWidgets.QWidget=None):
        super().__init__(parent)
        self.rows = 1

        self.widget = QtWidgets.QWidget(self)
        self.layout = QtWidgets.QGridLayout(self.widget)

        self.add_button = QtWidgets.QPushButton("Add")
        self.add_button.clicked.connect(self.add_entry)

        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setWidgetResizable(True)

        self.layout.addWidget(self.add_button)
        self.widget.setLayout(self.layout)
        self.setWidget(self.widget)
        self.add_entry()

    def add_entry(self):
        self.layout.removeWidget(self.add_button)

        data_label = QtWidgets.QLabel("Dependent Data", self)
        operator_label = QtWidgets.QLabel("Operator", self)
        value_label = QtWidgets.QLabel("Value", self)

        data_combobox = QtWidgets.QComboBox(self)
        data_combobox.addItems(["data1", "data2", "data3"])

        operator_combobox = QtWidgets.QComboBox(self)
        operator_combobox.addItems(["<", "<=", ">", ">=", "~=", "=="])
        value_line_edit = QtWidgets.QLineEdit(self)

        remove_button = QtWidgets.QPushButton("Remove", self)

        index = self.rows * 2

        def pop_row():
            self.layout.removeWidget(data_label)
            self.layout.removeWidget(operator_label)
            self.layout.removeWidget(value_label)

            self.layout.removeWidget(data_combobox)
            self.layout.removeWidget(operator_combobox)
            self.layout.removeWidget(value_line_edit)

            data_label.deleteLater()
            operator_label.deleteLater()
            value_label.deleteLater()

            data_combobox.deleteLater()
            operator_combobox.deleteLater()
            value_line_edit.deleteLater()
            remove_button.deleteLater()

            self.rows-= 1

        remove_button.clicked.connect(pop_row)

        self.layout.addWidget(data_label, index, 0)
        self.layout.addWidget(operator_label, index, 1)
        self.layout.addWidget(value_label, index, 2)

        self.layout.addWidget(data_combobox, index + 1, 0)
        self.layout.addWidget(operator_combobox, index + 1, 1)
        self.layout.addWidget(value_line_edit, index + 1, 2)
        self.layout.addWidget(remove_button, index + 1, 3)
        self.rows += 1
        self.layout.addWidget(self.add_button, index + 2, 0, 1, 2)

    def remove_row(self, index: int):
        pass

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    td = ToolDependencyArea()
    sys.exit(app.exec_())
