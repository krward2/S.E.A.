from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QPlainTextEdit, QGroupBox, QGridLayout, QScrollArea, QFileDialog
from PyQt5.QtCore import Qt
from controller import AbstractToolConfigurationCRUD, ToolConfigurationCRUD
from model import ToolConfiguration, ToolOptionArgument, OutputDataSpecification
from typing import List
import json

# Authored by Jacob Loosa. Last update: 24 March 2021, 10:47 PM MST.

class ToolSpecificationArea(QWidget):
    """
        The ToolSpecificationArea class is an extension of a QWidget superclass.

        This class addresses the following SRS Requirements:
            [SRS 17] - User Interface
            [SRS 70], [SRS 71], [SRS 72], [SRS 73] - Stimulus
    """

    def __init__(self, _id: str = None,
                 *, accept_function: callable = None,
                 cancel_function: callable = None):
        super().__init__()

        self.accept_function = accept_function
        self.cancel_function = cancel_function
        # TODO If _id is set, load existing configuration
        # Private attributes
        self._controller: AbstractToolConfigurationCRUD = ToolConfigurationCRUD # Static reference to concrete class
        self._name: QLineEdit = QLineEdit()
        self._description: QPlainTextEdit = QPlainTextEdit()
        self._path: QLineEdit = QLineEdit()
        self._path.setReadOnly(True)
        self._optarg_list: RemovableTextFieldList
        self._ods_list: RemovableTextFieldList
        self._button_accept: QPushButton = QPushButton("Accept")
        self._button_cancel: QPushButton = QPushButton("Cancel")
        # User Interface Shenanigans
        self._title = "Tool Specification"
        self.setWindowTitle(self._title)
        # Divide the UI into two sections - Manual Data Entry and File Import
        # Section 1: Manual Data Entry
        self._qGroupBoxManual: QGroupBox = QGroupBox("Manual Entry")
        # Section 1a: Tools Options and Arguments
        self._qGroupBoxManual_optargs: QGroupBox = QGroupBox("Options and Arguments")
        self._populateGroupBoxManual()
        # Section 2: Load File
        self._qGroupBoxAutomatic: QGroupBox = QGroupBox("Load Entry")
        self._populateGroupBoxAutomatic()
        # Stack both group boxes on top of each other in this window
        self._qGroupBoxMain: QGroupBox = QGroupBox(self._title)
        self._layoutMain: QGridLayout = QGridLayout()
        self._layoutMain.addWidget(self._qGroupBoxManual, 0, 0, 1, 3)
        self._layoutMain.addWidget(self._qGroupBoxAutomatic, 1, 0, 1, 3)
        self._layoutMain.setRowStretch(0, 1)
        self._layoutMain.addWidget(self._button_cancel, 3, 0)
        self._layoutMain.addWidget(self._button_accept, 3, 2)
        # Connect the accept and cancel buttons to their click functions
        self._button_accept.clicked.connect(self.on_final_accept)
        self._button_cancel.clicked.connect(self.on_final_cancel)
        self.setLayout(self._layoutMain)

    def on_final_accept(self) -> str:
        """
            Called when the user presses the "Accept" button
            Returns the _id of this tool configuration
        """
        # Core attributes
        name = self._name.text()
        desc = self._description.toPlainText()
        path = self._path.text()
        # Create Tool Config
        tool_config: ToolConfiguration = ToolConfiguration(name, desc, path)
        # Options and arguments
        [tool_config.add_tool_option_argument(ToolOptionArgument(*x.split())) for x in self._optarg_list.get_line_contents()]
        # Output Data Specifications
        [tool_config.add_output_data_specifications(OutputDataSpecification(*(x.split()))) for x in self._ods_list.get_line_contents()]
        ack, _id = self._controller.create_tool_configuration(tool_config)
        self._name.setText("")
        self._description.setPlainText("")
        self._path.setText("")
        self.accept_function()
        return _id

    def on_final_cancel(self):
        """
            Called when the user presses the "Cancel" button
        """
        self._name.setText("")
        self._description.setPlainText("")
        self._path.setText("")

        self.cancel_function()

    def _populateGroupBoxManual(self):
        """
            Populates the group box that will be used for manual data entry
        """
        layout: QGridLayout = QGridLayout()
        # TODO Add third column - usually "Select File" buttons
        # Row 1: Tool Name
        layout.addWidget(QLabel("Tool Name"), 0, 0)
        layout.addWidget(self._name, 0, 1, 1, 2)  # The 1 and 2 at the end are used to show that the text box spans 2 columns and one row. This is to make it go above the button below this row
        # Row 2: Tool Description
        layout.addWidget(QLabel("Tool Description"), 1, 0)
        layout.addWidget(self._description, 1, 1, 1, 2)
        # Row 3: Tool Path
        layout.addWidget(QLabel("Tool Path"), 2, 0)
        layout.addWidget(self._path, 2, 1)
        browse_button = QPushButton("Browse", self)
        browse_button.clicked.connect(self.browse_tool_path)
        layout.addWidget(browse_button, 2, 2)
        # Row 4: Option and Argument
        self._optarg_list = RemovableTextFieldList("Options and Arguments")
        layout.addWidget(self._optarg_list, 3, 0, 1, 3)
        layout.setRowStretch(3, 1)
        # Row 5: Output Data Specification
        self._ods_list = RemovableTextFieldList("Output Data Specification")
        layout.addWidget(self._ods_list, 4, 0, 1, 3)
        layout.setRowStretch(4, 1)
        self._qGroupBoxManual.setLayout(layout)

    def _populateGroupBoxAutomatic(self):
        layout: QGridLayout = QGridLayout()
        # Row 1: Tool Specification File
        layout.addWidget(QLabel("Tool Specification File"), 0, 0)
        self._file = QLineEdit(self)
        self._file.setReadOnly(True)
        layout.addWidget(self._file, 0, 1)
        browse_button = QPushButton("Browse", self)
        browse_button.clicked.connect(self.browse_tool_file)
        layout.addWidget(browse_button, 0, 2)
        self._qGroupBoxAutomatic.setLayout(layout)

    def browse_tool_path(self):
        filename = QFileDialog.getOpenFileName(self, "Open Tool Path", "/usr/bin")[0]
        self._path.setText(filename)

    def browse_tool_file(self):
        filename = QFileDialog.getOpenFileName(self, "Open Tool Specification File", ".")[0]
        tool_json = json.load(open(filename))
        self._name.setText(tool_json["name"])
        self._description.setText(tool_json["description"])
        self._path.setText(tool_json["path"])


class RemovableTextFieldList(QGroupBox):
    """
    Creates a scrollable list of entries with an "Add" button at the bottom
    Each Entry has an associated "Remove" Button
    """

    def __init__(self, name: str):
        super().__init__(name)
        # Create UI elements
        self._qlines: List[QLineEdit] = list()
        self._scrollbox: QScrollArea = QScrollArea()
        self._widget: QWidget = QWidget()
        self._scroll_layout: QGridLayout = QGridLayout()
        self._group_layout: QGridLayout = QGridLayout()
        # The Add Button to Add an Entry
        self._add_button = QPushButton("Add")
        self._add_button.clicked.connect(self.add_entry)
        self._scroll_layout.addWidget(self._add_button, 0, 1)
        # Apply UI Policies
        self._scrollbox.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self._scrollbox.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scrollbox.setWidgetResizable(True)
        # Assign the layout to the widget
        self._widget.setLayout(self._scroll_layout)
        # Assign the widget to the scroll box
        self._scrollbox.setWidget(self._widget)
        # Add everything to the group box
        self._group_layout.addWidget(self._scrollbox, 0, 0, 3, 3)
        self.setLayout(self._group_layout)

    def add_entry(self):
        qline: QLineEdit = QLineEdit()
        qbutton: QPushButton = QPushButton("Remove")
        index = len(self._qlines)
        # Method to be used when the remove button is pressed
        def pop_widget():
            self._scroll_layout.removeWidget(qline)
            self._scroll_layout.removeWidget(qbutton)
            self._qlines.remove(qline)
            qline.deleteLater()
            qbutton.deleteLater()
        qbutton.clicked.connect(pop_widget)
        # Remove the add button so we can move it to the bottom
        self._scroll_layout.removeWidget(self._add_button)
        # Add the buttons to the list
        self._qlines.append(qline)
        # Add the button and field
        self._scroll_layout.addWidget(qline, index, 0, 1, 2)
        self._scroll_layout.addWidget(qbutton, index, 2, 1, 1)
        # Add the button back in the center
        self._scroll_layout.addWidget(self._add_button)

    def get_line_contents(self) -> List[str]:
        return [x.text() for x in self._qlines]


# Make module runnable for testing purposes.
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    widget = ToolSpecificationArea()
    widget.setGeometry(300, 400, 600, 800)
    widget.show()

    sys.exit(app.exec_())