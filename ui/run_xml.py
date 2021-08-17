from PyQt5 import QtCore, QtGui, QtWidgets


class XMLReport(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget):
        super().__init__(parent)

        layout = QtWidgets.QVBoxLayout(self)

        upper_group_box = QtWidgets.QGroupBox("Automatic", self)
        upper_layout = QtWidgets.QGridLayout(upper_group_box)
        report_name_label = QtWidgets.QLabel("Report Name", upper_group_box)
        report_desc_label = QtWidgets.QLabel("Description of Run", upper_group_box)
        report_run_label = QtWidgets.QLabel("Run", upper_group_box)
        self.report_name_line_edit = QtWidgets.QLineEdit(upper_group_box)
        self.report_desc_line_edit = QtWidgets.QPlainTextEdit(upper_group_box)
        self.report_run_combobox = QtWidgets.QComboBox(upper_group_box)

        upper_layout.addWidget(report_name_label, 0, 0)
        upper_layout.addWidget(report_desc_label, 1, 0)
        upper_layout.addWidget(report_run_label, 2, 0)
        upper_layout.addWidget(self.report_name_line_edit, 0, 1, 2, 1)
        upper_layout.addWidget(self.report_desc_line_edit, 1, 1, 2, 1)
        upper_layout.addWidget(self.report_run_combobox, 2, 1, 2, 1)

        lower_group_box = QtWidgets.QGroupBox("Manual", self)
        lower_layout = QtWidgets.QGridLayout(lower_group_box)
        run_label = QtWidgets.QLabel("Run", lower_group_box)
        scan_label = QtWidgets.QLabel("Scan", lower_group_box)
        self.run_combobox = QtWidgets.QComboBox(lower_group_box)
        self.scan_combobox = QtWidgets.QComboBox(lower_group_box)
        self.remove_button = QtWidgets.QPushButton("Remove", lower_group_box)

        lower_layout.addWidget(run_label, 0, 0)
        lower_layout.addWidget(self.run_combobox, 0, 1)
        lower_layout.addWidget(scan_label, 0, 2)
        lower_layout.addWidget(self.scan_combobox, 0, 3)
        lower_layout.addWidget(self.remove_button, 0, 4)

        self.add_button = QtWidgets.QPushButton("Add", self)
        self.generate_button = QtWidgets.QPushButton("Generate", self)
        self.cancel_button = QtWidgets.QPushButton("Cancel", self)

        layout.addWidget(upper_group_box)
        layout.addWidget(lower_group_box)
        layout.addWidget(self.add_button)
        layout.addWidget(self.generate_button)
        layout.addWidget(self.cancel_button)
        self.setLayout(layout)
        self.show()
