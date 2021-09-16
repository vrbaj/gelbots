from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QMainWindow, QLabel, QLineEdit, QPushButton, QInputDialog
from PyQt5.QtCore import QSize, QRect, pyqtSignal

import formation_optimization


class FormationWindow(QMainWindow):
    change_params = pyqtSignal(list, list)

    def __init__(self):
        super(FormationWindow, self).__init__()
        self.disksList = []
        self.targetsList = []
        self.automode_status = False

        self.setFixedSize(QSize(300, 500))
        self.setWindowTitle("Formation settings")
        self.disk_label = QLabel(self)
        self.disk_label.setGeometry(QRect(10, 0, 80, 20))
        self.disk_label.setText("Disks")
        self.disksListView = QtWidgets.QListView(self)
        self.disksListView.setGeometry(QRect(10, 25, 80, 400))
        self.disksModel = QtGui.QStandardItemModel()
        self.disksListView.setModel(self.disksModel)

        self.target_label = QLabel(self)
        self.target_label.setGeometry(QRect(100, 0, 80, 20))
        self.target_label.setText("Targets")
        self.targetsListView = QtWidgets.QListView(self)
        self.targetsListView.setGeometry(QRect(100, 25, 80, 400))
        self.targetsModel = QtGui.QStandardItemModel()
        self.targetsListView.setModel(self.targetsModel)

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
            disk_order, target_order = formation_optimization.optimize_formation(self.disksList, self.targetsList, 60)
            print(self.disksList, self.targetsList)
            print("order: ", disk_order, "target order: ", target_order)
            self.disksModel.clear()
            self.targetsModel.clear()
            for item in disk_order:
                qt_item = QtGui.QStandardItem(str(self.disksList[item]))
                self.disksModel.appendRow(qt_item)
            for item in target_order:
                qt_item = QtGui.QStandardItem(str(self.targetsList[item]))
                self.targetsModel.appendRow(qt_item)
            self.change_params.emit(self.disksList, self.targetsList)
        else:
            error_dialog = QtWidgets.QErrorMessage()
            error_dialog.showMessage("It is not possible to optimize in automode!")
            error_dialog.setWindowTitle("Error")
            error_dialog.exec_()

    def remove_disk(self):
        index_list = []
        for model_index in self.disksListView.selectionModel().selectedRows():
            index = QtCore.QPersistentModelIndex(model_index)
            index_list.append(index)
        for index in index_list:
            self.disksModel.removeRow(index.row())
        self.get_targets_disks()

    def remove_target(self):
        index_list = []
        for model_index in self.targetsListView.selectionModel().selectedRows():
            index = QtCore.QPersistentModelIndex(model_index)
            index_list.append(index)
        for index in index_list:
            self.targetsModel.removeRow(index.row())
        self.get_targets_disks()

    def add_disk(self, disk):
        item = QtGui.QStandardItem(disk)
        self.disksModel.appendRow(item)
        self.get_targets_disks()

    def get_targets_disks(self):
        self.disksList = []
        self.targetsList = []
        for index in range(self.disksModel.rowCount()):
            item = self.disksModel.item(index)
            raw_list = list(map(int, item.text().strip('][').split(', ')))
            self.disksList.append(raw_list)
        for index in range(self.targetsModel.rowCount()):
            item = self.targetsModel.item(index)
            raw_list = list(map(int, item.text().strip('][').split(', ')))
            self.targetsList.append(raw_list)
        self.change_params.emit(self.disksList, self.targetsList)

    def add_target(self, disk):
        item = QtGui.QStandardItem(disk)
        self.targetsModel.appendRow(item)
        self.get_targets_disks()

    def add_disk_text(self):
        text, ok_pressed = QInputDialog.getText(self, "Input disk coordinates [x, y]", "Coordinates [x, y]:",
                                                QLineEdit.Normal, "")
        if ok_pressed and text != '':
            item = QtGui.QStandardItem(text)
            self.disksModel.appendRow(item)
        self.get_targets_disks()

    def add_target_text(self):
        text, ok_pressed = QInputDialog.getText(self, "Input target coordinates [x, y]", "Coordinates [x, y]:",
                                                QLineEdit.Normal, "")
        if ok_pressed and text != '':
            item = QtGui.QStandardItem(text)
            self.targetsModel.appendRow(item)
        self.get_targets_disks()

    def refill_lists(self):
        try:
            self.disksModel.clear()
            self.targetsModel.clear()
            for index in range(len(self.disksList)):
                self.disksModel.appendRow(QtGui.QStandardItem(str(self.disksList[index])))
            for index in range(len(self.targetsList)):
                self.targetsModel.appendRow(QtGui.QStandardItem(str(self.targetsList[index])))
        except Exception as ex:
            print(ex)