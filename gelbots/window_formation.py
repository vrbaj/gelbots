"""
This module implements the window for formation specification and its optimalization.
"""

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QMainWindow, QLabel, QLineEdit, QPushButton, QInputDialog
from PyQt5.QtCore import QSize, QRect, pyqtSignal

import gelbots.formation_optimization


class FormationWindow(QMainWindow):
    """
    Class that defines the Formation Window and its properties.
    """

    # pylint: disable=too-many-instance-attributes
    # 14 is reasonable in this case.

    change_params = pyqtSignal(list, list)

    def __init__(self):
        super().__init__()
        self.disks_list = []
        self.targets_list = []
        self.automode_status = False

        self.setFixedSize(QSize(300, 500))
        self.setWindowTitle("Formation settings")

        # labels
        self.disk_label = QLabel(self)
        self.target_label = QLabel(self)
        self.__init_labels()

        # buttons
        self.add_disk_button = QPushButton(self)
        self.remove_disk_button = QPushButton(self)
        self.add_target_button = QPushButton(self)
        self.remove_target_button = QPushButton(self)
        self.optimize_button = QPushButton(self)
        self.__init_buttons()

        # lists
        self.disks_list_view = QtWidgets.QListView(self)
        self.disks_list_view.setGeometry(QRect(10, 25, 80, 400))
        self.disks_model = QtGui.QStandardItemModel()
        self.disks_list_view.setModel(self.disks_model)

        self.targets_list_view = QtWidgets.QListView(self)
        self.targets_list_view.setGeometry(QRect(100, 25, 80, 400))
        self.targets_model = QtGui.QStandardItemModel()
        self.targets_list_view.setModel(self.targets_model)

    def __init_labels(self):
        """Function that initializes all labels."""
        # disk label
        self.disk_label.setGeometry(QRect(10, 0, 80, 20))
        self.disk_label.setText("Disks")
        # target label
        self.target_label.setGeometry(QRect(100, 0, 80, 20))
        self.target_label.setText("Targets")

    def __init_buttons(self):
        """Function that initializes all buttons."""
        # add disk button
        self.add_disk_button.setGeometry(QRect(200, 300, 100, 30))
        self.add_disk_button.setToolTip("Click to add disk coordinates")
        self.add_disk_button.setText("Add disk")
        self.add_disk_button.clicked.connect(self.add_disk_text)
        # remove disk button
        self.remove_disk_button.setGeometry(QRect(200, 380, 100, 30))
        self.remove_disk_button.setToolTip("Click to remove selected disk coordinates")
        self.remove_disk_button.setText("Remove disk")
        self.remove_disk_button.clicked.connect(self.remove_disk)
        # add target button
        self.add_target_button.setGeometry(QRect(200, 340, 100, 30))
        self.add_target_button.setToolTip("Click to add target coordinates")
        self.add_target_button.setText("Add target")
        self.add_target_button.clicked.connect(self.add_target_text)
        # remove target button
        self.remove_target_button.setGeometry(QRect(200, 420, 100, 30))
        self.remove_target_button.setToolTip("Click to remove selected target coordinates")
        self.remove_target_button.setText("Remove target")
        self.remove_target_button.clicked.connect(self.remove_target)
        # optimize button
        self.optimize_button.setGeometry(QRect(200, 460, 100, 30))
        self.optimize_button.setToolTip("Click to optimize formation making")
        self.optimize_button.setText("Optimize")
        self.optimize_button.clicked.connect(self.optimize_order)

    def optimize_order(self):
        """
        This function call the optimization function and fills lists with
        disks and targets coordinates according to optimization result.
        Signal with new disk list and disk order is emited to gelbots.py.
        :return:
        """
        if not self.automode_status:
            disk_order, target_order = formation_optimization.optimize_formation(
                self.disks_list, self.targets_list, 60)
            self.disks_model.clear()
            self.targets_model.clear()
            for item in disk_order:
                qt_item = QtGui.QStandardItem(str(self.disks_list[item]))
                self.disks_model.appendRow(qt_item)
            for item in target_order:
                qt_item = QtGui.QStandardItem(str(self.targets_list[item]))
                self.targets_model.appendRow(qt_item)
            self.change_params.emit(self.disks_list, self.targets_list)
        else:
            error_dialog = QtWidgets.QErrorMessage()
            error_dialog.showMessage("It is not possible to optimize in automode!")
            error_dialog.setWindowTitle("Error")
            error_dialog.exec_()

    def remove_disk(self):
        """Function to remove selected disk from the list of disks and refills the
        list view with new list of disks (via function get_targets_disks)."""
        index_list = []
        for model_index in self.disks_list_view.selectionModel().selectedRows():
            index = QtCore.QPersistentModelIndex(model_index)
            index_list.append(index)
        for index in index_list:
            self.disks_model.removeRow(index.row())
        self.get_targets_disks()

    def remove_target(self):
        """Function to remove selected target from the list of disks and refills the
        list view with new list of targets (via function get_targets_disks)."""
        index_list = []
        for model_index in self.targets_list_view.selectionModel().selectedRows():
            index = QtCore.QPersistentModelIndex(model_index)
            index_list.append(index)
        for index in index_list:
            self.targets_model.removeRow(index.row())
        self.get_targets_disks()
        # TODO update CORE!!

    def add_disk(self, disk):
        """
        Function to append new disk to list of disks for formation and to
        add this disk to disk list view.
        :param disk: Coordinates of disk (string)
        :return:
        """
        item = QtGui.QStandardItem(disk)
        self.disks_model.appendRow(item)
        self.get_targets_disks()

    def get_targets_disks(self):
        """
        This function refreshes the lists with disks and targets as same
        as according list views. Signal with new disks and targets list
        is then sent to gelbots.py
        :return:
        """
        self.disks_list = []
        self.targets_list = []
        for index in range(self.disks_model.rowCount()):
            item = self.disks_model.item(index)
            raw_list = list(map(int, item.text().strip('][').split(', ')))
            self.disks_list.append(raw_list)
        for index in range(self.targets_model.rowCount()):
            item = self.targets_model.item(index)
            raw_list = list(map(int, item.text().strip('][').split(', ')))
            self.targets_list.append(raw_list)
        self.change_params.emit(self.disks_list, self.targets_list)

    def add_target(self, target):
        """
        Function to append new target to list of targets for formation and to
        add this target to target list view.
        :param target: Coordinates of target (string)
        :return:
        """
        item = QtGui.QStandardItem(target)
        self.targets_model.appendRow(item)
        self.get_targets_disks()

    def add_disk_text(self):
        """
        Function that shows the input dialog to insert the disk coordinates
        as the string "[x, y]". Coordinates are then added to disks list view.
        :return:
        """
        text, ok_pressed = QInputDialog.getText(self,
                                                "Input disk coordinates [x, y]",
                                                "Coordinates [x, y]:",
                                                QLineEdit.Normal, "")
        if ok_pressed and text != '':
            item = QtGui.QStandardItem(text)
            self.disks_model.appendRow(item)
        self.get_targets_disks()

    def add_target_text(self):
        """
        Function that shows the input dialog to insert the target coordinates
        as the string "[x, y]". Coordinates are then added to targets list view.
        :return:
        """
        text, ok_pressed = QInputDialog.getText(self,
                                                "Input target coordinates [x, y]",
                                                "Coordinates [x, y]:",
                                                QLineEdit.Normal, "")
        if ok_pressed and text != '':
            item = QtGui.QStandardItem(text)
            self.targets_model.appendRow(item)
        self.get_targets_disks()

    def refill_lists(self):
        """
        This function empties the list views and fills them with items from
        lists with disks and targets.
        :return:
        """
        self.disks_model.clear()
        self.targets_model.clear()
        for disk in self.disks_list:
            self.disks_model.appendRow(QtGui.QStandardItem(str(disk)))
        for target in self.targets_list:
            self.targets_model.appendRow(QtGui.QStandardItem(str(target)))
