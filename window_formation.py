"""
This module implements the window for formation specification and its optimalization.
"""

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QMainWindow, QLabel, QLineEdit, QPushButton, QInputDialog
from PyQt5.QtCore import QSize, QRect, pyqtSignal

import formation_optimization


class FormationWindow(QMainWindow):
    """
    Class that defines the Formation Window and its properties.
    """
    change_params = pyqtSignal(list, list)

    def __init__(self):
        super(FormationWindow, self).__init__()
        self.disks_list = []
        self.targets_list = []
        self.automode_status = False

        self.setFixedSize(QSize(300, 500))
        self.setWindowTitle("Formation settings")
        self.disk_label = QLabel(self)
        self.disk_label.setGeometry(QRect(10, 0, 80, 20))
        self.disk_label.setText("Disks")
        self.disks_list_view = QtWidgets.QListView(self)
        self.disks_list_view.setGeometry(QRect(10, 25, 80, 400))
        self.disks_model = QtGui.QStandardItemModel()
        self.disks_list_view.setModel(self.disks_model)

        self.target_label = QLabel(self)
        self.target_label.setGeometry(QRect(100, 0, 80, 20))
        self.target_label.setText("Targets")
        self.targets_list_view = QtWidgets.QListView(self)
        self.targets_list_view.setGeometry(QRect(100, 25, 80, 400))
        self.targetsModel = QtGui.QStandardItemModel()
        self.targets_list_view.setModel(self.targetsModel)

        self.add_disk_button = QPushButton(self)
        self.add_disk_button.setGeometry(QRect(200, 300, 100, 30))
        self.add_disk_button.setToolTip("Click to add disk coordinates")
        self.add_disk_button.setText("Add disk")
        self.add_disk_button.clicked.connect(self.add_disk_text)

        self.remove_disk_button = QPushButton(self)
        self.remove_disk_button.setGeometry(QRect(200, 380, 100, 30))
        self.remove_disk_button.setToolTip("Click to remove selected disk coordinates")
        self.remove_disk_button.setText("Remove disk")
        self.remove_disk_button.clicked.connect(self.remove_disk)

        self.add_target_button = QPushButton(self)
        self.add_target_button.setGeometry(QRect(200, 340, 100, 30))
        self.add_target_button.setToolTip("Click to add target coordinates")
        self.add_target_button.setText("Add target")
        self.add_target_button.clicked.connect(self.add_target_text)

        self.remove_target_button = QPushButton(self)
        self.remove_target_button.setGeometry(QRect(200, 420, 100, 30))
        self.remove_target_button.setToolTip("Click to remove selected target coordinates")
        self.remove_target_button.setText("Remove target")
        self.remove_target_button.clicked.connect(self.remove_target)

        self.optimize_button = QPushButton(self)
        self.optimize_button.setGeometry(QRect(200, 460, 100, 30))
        self.optimize_button.setToolTip("Click to optimize formation making")
        self.optimize_button.setText("Optimize")
        self.optimize_button.clicked.connect(self.optimize_order)

    def optimize_order(self):
        if not self.automode_status:
            disk_order, target_order = formation_optimization.optimize_formation(
                self.disks_list, self.targets_list, 60)
            self.disks_model.clear()
            self.targetsModel.clear()
            for item in disk_order:
                qt_item = QtGui.QStandardItem(str(self.disks_list[item]))
                self.disks_model.appendRow(qt_item)
            for item in target_order:
                qt_item = QtGui.QStandardItem(str(self.targets_list[item]))
                self.targetsModel.appendRow(qt_item)
            self.change_params.emit(self.disks_list, self.targets_list)
        else:
            error_dialog = QtWidgets.QErrorMessage()
            error_dialog.showMessage("It is not possible to optimize in automode!")
            error_dialog.setWindowTitle("Error")
            error_dialog.exec_()

    def remove_disk(self):
        index_list = []
        for model_index in self.disks_list_view.selectionModel().selectedRows():
            index = QtCore.QPersistentModelIndex(model_index)
            index_list.append(index)
        for index in index_list:
            self.disks_model.removeRow(index.row())
        self.get_targets_disks()

    def remove_target(self):
        index_list = []
        for model_index in self.targets_list_view.selectionModel().selectedRows():
            index = QtCore.QPersistentModelIndex(model_index)
            index_list.append(index)
        for index in index_list:
            self.targetsModel.removeRow(index.row())
        self.get_targets_disks()

    def add_disk(self, disk):
        item = QtGui.QStandardItem(disk)
        self.disks_model.appendRow(item)
        self.get_targets_disks()

    def get_targets_disks(self):
        self.disks_list = []
        self.targets_list = []
        for index in range(self.disks_model.rowCount()):
            item = self.disks_model.item(index)
            raw_list = list(map(int, item.text().strip('][').split(', ')))
            self.disks_list.append(raw_list)
        for index in range(self.targetsModel.rowCount()):
            item = self.targetsModel.item(index)
            raw_list = list(map(int, item.text().strip('][').split(', ')))
            self.targets_list.append(raw_list)
        self.change_params.emit(self.disks_list, self.targets_list)

    def add_target(self, disk):
        item = QtGui.QStandardItem(disk)
        self.targetsModel.appendRow(item)
        self.get_targets_disks()

    def add_disk_text(self):
        text, ok_pressed = QInputDialog.getText(self,
                                                "Input disk coordinates [x, y]",
                                                "Coordinates [x, y]:",
                                                QLineEdit.Normal, "")
        if ok_pressed and text != '':
            item = QtGui.QStandardItem(text)
            self.disks_model.appendRow(item)
        self.get_targets_disks()

    def add_target_text(self):
        text, ok_pressed = QInputDialog.getText(self,
                                                "Input target coordinates [x, y]",
                                                "Coordinates [x, y]:",
                                                QLineEdit.Normal, "")
        if ok_pressed and text != '':
            item = QtGui.QStandardItem(text)
            self.targetsModel.appendRow(item)
        self.get_targets_disks()

    def refill_lists(self):
        try:
            self.disks_model.clear()
            self.targetsModel.clear()
            for disk in self.disks_list:
                self.disks_model.appendRow(QtGui.QStandardItem(str(disk)))
            for target in self.targets_list:
                self.targetsModel.appendRow(QtGui.QStandardItem(str(target)))
        except Exception as ex:
            print(ex)
