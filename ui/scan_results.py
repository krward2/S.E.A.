from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QTabBar, QTabWidget, QStylePainter, QStyleOptionTab, QStyle, \
    QVBoxLayout, QLabel, QPlainTextEdit
from typing import Union
from model import RunResult
from controller import RunResultCRUD

'''
@author Kenneth Ward
This file contains classes and code related to the Scan Result Area
'''


class ScanResults(QTabWidget):
    """
        The ScanResult class is responsible for adding tabs, and utilizes the QTabBar
        defined in the ScanTab class.
        The following SRS requirements are addressed:
        SRS[10]
    """

    def __init__(self, run_name: str = '', timestamp: str = ''):
        super().__init__()

        # Run name and timestamp used to retrieve ScanResults from db
        self._run_name: str = run_name
        self._timestamp: str = timestamp

        # Configure tab bar
        self.setTabBar(ScanTabBar(self))
        self.setTabPosition(QTabWidget.West)

        # List for updates to RunResults (ScanResults contained on RunResult)
        RunResultCRUD.get_instance().dataChanged.connect(self.update_data)

        if run_name and timestamp:
            self.update_data()
        else:
            self.addExamples()

    # Adds example tabs for demo purposes
    def addExamples(self):
        exampleTabLabels = ['Scan ' + str(i) for i in range(1, 21)]
        for tabLabel in exampleTabLabels:
            tab = QWidget()
            tabLayout = QVBoxLayout()
            tabLayout.addWidget(QLabel(tabLabel + ' Result'))
            tab.setLayout(tabLayout)

            self.addTab(tab, tabLabel)

    # Intended as a callback for RunResultCRUD dataChanged signal
    def update_data(self):
        # For each ScanResult inside the proper RunResult add a tab containing tool output
        run_result = RunResultCRUD.get_instance().read_run_result(self._run_name, self._timestamp)
        if run_result:
            scan_results = run_result.get_scan_results()
            # Remove tabs
            for i in reversed(range(self.count())):
                self.widget(i).setParent(None)
            # Re-add tabs
            for scan_result in scan_results:
                tab = QWidget()
                tab_layout = QVBoxLayout()
                print(scan_result.get_formatted_scan_output())
                qpt = QPlainTextEdit(scan_result.get_formatted_scan_output())
                qpt.setReadOnly(True)
                tab_layout.addWidget(qpt)
                tab.setLayout(tab_layout)

                self.addTab(tab, scan_result.get_scan_name())


class ScanTabBar(QTabBar):
    """
    The ScanTabBar class defines custom behavior for the QTabBar class. Namely,
    it allows the QTabBar to be painted vertically and display Tabs and Tab labels
    horizontally.
    This class addresses SRS requirements:
    SRS[10]
    """

    def tabSizeHint(self, index):
        s = QTabBar.tabSizeHint(self, index)
        s.transpose()
        return s

    def paintEvent(self, event):
        painter = QStylePainter(self)
        opt = QStyleOptionTab()

        for i in range(self.count()):
            self.initStyleOption(opt, i)
            painter.drawControl(QStyle.CE_TabBarTabShape, opt)
            painter.save()

            s = opt.rect.size()
            s.transpose()
            r = QtCore.QRect(QtCore.QPoint(), s)
            r.moveCenter(opt.rect.center())
            opt.rect = r

            c = self.tabRect(i).center()
            painter.translate(c)
            painter.rotate(90)
            painter.translate(-c)
            painter.drawControl(QStyle.CE_TabBarTabLabel, opt);
            painter.restore()


# Testing driver
if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    w = ScanResults()
    w.show()

    sys.exit(app.exec_())
