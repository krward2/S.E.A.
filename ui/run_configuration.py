from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QPlainTextEdit, QGroupBox, \
    QGridLayout, QComboBox, QVBoxLayout, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt

from controller import RunConfigurationCRUD, ToolConfigurationCRUD
from model import run_configuration, ScanConfiguration, ToolConfiguration
from model import Target, MutualExclusivityError, DuplicateIPError

from typing import List
from functools import partial
import json

'''
@author Kenneth Ward
This file contains classes and code related to the Run Configuration Area
'''


class RunConfiguration(QWidget):
    """
        The RunConfigurationArea class is an extension of the QWidget superclass.
        The class addresses the following SRS User Interface Requirements:
        [SRS 7]
    """

    def __init__(self, parent: QWidget = None,
                 *, accept_function: callable = None,
                 cancel_function: callable = None):
        super().__init__()
        self._title = "Run Configuration"
        self.setWindowTitle(self._title)
        self.accept_function = accept_function
        self.cancel_function = cancel_function

        # Manual Configuration GroupBox created and populated
        self._qGroupBoxManualConfig: QGroupBox = QGroupBox('Manual Configuration')
        self._populateManualConfigGroupBox()

        # Select Configuration File GroupBox created and populated
        self._qGroupBoxSelectConfig: QGroupBox = QGroupBox('Select Configuration File')
        self._populateSelectConfigFileGroupBox()

        # Assemble Manual Config and Select config into outer GroupBox
        self._qGroupBoxMain: QGroupBox = QGroupBox(self._title)
        self._layoutMain: QGridLayout = QGridLayout()
        self._layoutMain.addWidget(self._qGroupBoxManualConfig, 0, 0)
        self._layoutMain.addWidget(self._qGroupBoxSelectConfig, 1, 0)
        self._layoutMain.setRowStretch(2, 1)
        accept_button: QPushButton = QPushButton('Accept', self)
        accept_button.clicked.connect(self.accept_configuration)
        self._layoutMain.addWidget(accept_button, 3, 0)
        cancel_button: QPushButton = QPushButton("Cancel", self)
        cancel_button.clicked.connect(self.cancel_function)
        self._layoutMain.addWidget(cancel_button, 4, 0)
        self.setLayout(self._layoutMain)

    # Initializes and places the UI elements of the Manual Configuration Areas
    def _populateManualConfigGroupBox(self):
        layout: QGridLayout = QGridLayout()

        self._runNameText: QLineEdit = QLineEdit()
        layout.addWidget(QLabel("Run Name"), 0, 0)
        layout.addWidget(self._runNameText, 0, 1, 1, 2)

        self._runDescriptionText: QPlainTextEdit = QPlainTextEdit()
        layout.addWidget(QLabel("Run Description"), 1, 0)
        layout.addWidget(self._runDescriptionText, 1, 1, 1, 2)

        self._whitelistText: QPlainTextEdit = QPlainTextEdit()
        layout.addWidget(QLabel("Whitelisted IP Target"), 2, 0)
        layout.addWidget(self._whitelistText, 2, 1, 1, 2)

        self._blacklistText: QPlainTextEdit = QPlainTextEdit()
        layout.addWidget(QLabel("Blacklisted IP Target"), 3, 0)
        layout.addWidget(self._blacklistText, 3, 1, 1, 2)

        self._scan_type_list: ScanTypeDropdownList = ScanTypeDropdownList()
        layout.addWidget(self._scan_type_list, 0, 3, 4, 1)

        self._qGroupBoxManualConfig.setLayout(layout)

    # Initializes and places the UI elements of the Manual Configuration Areas
    def _populateSelectConfigFileGroupBox(self):
        layout: QGridLayout = QGridLayout()

        browse_button = QPushButton('Browse')
        browse_button.clicked.connect(self.browse_run_path)
        layout.addWidget(QLabel('Run Configuration Path'), 0, 0)
        layout.addWidget(QLineEdit(), 0, 1, 1, 1)
        layout.addWidget(browse_button, 0, 2)

        self._qGroupBoxSelectConfig.setLayout(layout)

    def browse_run_path(self):
        filename = QFileDialog.getOpenFileName(self, "Open Run Configuration File", ".", "*.json")[0]
        if filename:
            run_config = json.load(open(filename))
            self._runNameText.setText(run_config["name"])
            self._runDescriptionText.setPlainText(run_config["description"])
            self._whitelistText.setPlainText(run_config["target"]["whitelist"])
            self._blacklistText.setPlainText(run_config["target"]["blacklist"])

    def accept_configuration(self):

        whitelist: List[str] = [ip.strip() for ip in self._whitelistText.toPlainText().split(',')]
        blacklist: List[str] = [ip.strip() for ip in self._blacklistText.toPlainText().split(',')]
        target: Target = Target()

        # Error Checks
        try:
            for ip in whitelist:
                target.add_to_whitelist(ip)
        except DuplicateIPError as e:
            qem = QMessageBox()
            qem.setWindowTitle("Error")
            qem.setText(str(e))
            qem.exec_()
            return

        try:
            for ip in blacklist:
                target.add_to_blacklist(ip)
        except DuplicateIPError as e:
            qem = QMessageBox()
            qem.setWindowTitle("Error")
            qem.setText(str(e))
            qem.exec_()
            return

        except MutualExclusivityError as e:
            qem = QMessageBox()
            qem.setWindowTitle("Error")
            qem.setText(str(e))
            qem.exec_()
            return

        if not self._scan_type_list._added_scan_types:
            qem = QMessageBox()
            qem.setWindowTitle("Error")
            qem.setText("No Scans Selected")
            qem.exec_()
            return

        run_name: str = self._runNameText.text()
        self._runNameText.setText('')
        run_description: str = self._runDescriptionText.toPlainText()
        self._runDescriptionText.setPlainText('')
        new_run_config: RunConfiguration = run_configuration.RunConfiguration(target, run_name, run_description)
        self._whitelistText.setPlainText('')
        self._blacklistText.setPlainText('')
        for scan_type in self._scan_type_list._added_scan_types:
            new_run_config.add_scan_configuration(ScanConfiguration(scan_type.get_tool_name(), scan_type))



        controller: RunConfigurationCRUD = RunConfigurationCRUD.get_instance()
        controller.create_run_configuration(new_run_config)
        if self.accept_function:
            self.accept_function()


class ScanTypeDropdownList(QWidget):
    '''
        The ScanTypeDropdownList provides a dropdown menu of available scans for
        addition to a Run and lists all scans added. Meant for placement in the Run Configuration Area.
        This class addresses the following SRS requirements: SRS[7].f, SRS[7].g, SRS[66], SRS[67]
    '''
    def __init__(self):
        super().__init__()

        # Dropdown menu contents
        self._scan_types: List[ToolConfiguration] = list()
        # Scans added to the run
        self._added_scan_types: List[ToolConfiguration] = list()

        # Make initial add drop down menu
        self._scan_type_label: QLabel = QLabel('Scan Type')
        self._dropdown: ScanDropDown = ScanDropDown()
        self.load_scan_types()
        self._add_button: QPushButton = QPushButton('Add')


        # Connect add button
        self._add_button.clicked.connect(self.add_scan_type)

        # Set layout
        self._layout: QGridLayout = QGridLayout()
        self._layout.addWidget(self._scan_type_label, 0, 0)
        self._layout.addWidget(self._dropdown, 0, 1)
        self._layout.addWidget(self._add_button, 0, 2)

        # Makes two columns one for the scan names and another for associated remove buttons
        self._added_scans_layout: QVBoxLayout = QVBoxLayout()
        self._remove_buttons_layout: QVBoxLayout = QVBoxLayout()
        self._layout.addLayout(self._added_scans_layout, 1, 1)
        self._layout.addLayout(self._remove_buttons_layout, 1, 2)

        # Format and set layout
        self._layout.setAlignment(Qt.AlignTop)
        self.setLayout(self._layout)

        #Gets notified of dataChanged signals from ToolConfigurationCRUD
        ToolConfigurationCRUD.NOTIFIER.dataChanged.connect(self.update_data)

    def add_scan_type(self):
        new_scan_type_name: str = str(self._dropdown.currentText())
        new_scan_type = [scan_type for scan_type in self._scan_types if scan_type.get_tool_name() == new_scan_type_name][0]
        self._added_scan_types.append(new_scan_type)

        self._added_scans_layout.addWidget(QLabel(new_scan_type_name))
        remove_button: QPushButton = QPushButton('Remove')
        remove_button.clicked.connect(partial(self.remove_scan_type, remove_button))
        self._remove_buttons_layout.addWidget(remove_button)

    # Removes the associated row in the list of added scans
    def remove_scan_type(self, button):
        scan_index: int = self._remove_buttons_layout.indexOf(button)

        self._added_scans_layout.itemAt(scan_index).widget().setParent(None)
        self._remove_buttons_layout.itemAt(scan_index).widget().setParent(None)
        del self._added_scan_types[scan_index]
        # TODO Connect to database

    def load_scan_types(self):
        self._scan_types: List[ToolConfiguration] = ToolConfigurationCRUD.read_all_tool_configurations()
        if self._scan_types:
            for scan in self._scan_types:
                self._dropdown.addItem(scan.get_tool_name())

    def update_data(self):
        self._scan_types = ToolConfigurationCRUD.read_all_tool_configurations()

class ScanDropDown (QComboBox):
    def __init__(self):
        super().__init__()
        self._notifier = ToolConfigurationCRUD.NOTIFIER.get_instance()
        self._notifier.dataChanged.connect(self.update_data)

    def update_data(self):
        self.clear()

        scan_configs = ToolConfigurationCRUD.read_all_tool_configurations()
        scan_config_names = [scan_config.get_tool_name() for scan_config in scan_configs]

        for scan_config_name in scan_config_names:
            print(scan_config_name)
            self.addItem(scan_config_name)

        self.update()

# Testing driver
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    widget = RunConfiguration()
    widget.setGeometry(300, 400, 900, 800)
    widget.show()

    sys.exit(app.exec_())
