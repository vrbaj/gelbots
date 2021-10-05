"""
Implements Factory pattern for Qt graphical object creation.
"""
from PyQt5.QtWidgets import QLabel, QPushButton, QLineEdit
from PyQt5.QtGui import QIntValidator, QDoubleValidator


class QtFactory:
    """
    Factory for PyQt5 objects that are added to windows.
    """
    # TODO replace label, button etc by general object_like and add single return statement

    @staticmethod
    def get_object(object_type, window, **kwargs):
        if object_type == QLabel:
            # create QLabel
            label = QLabel(window)
            label.setGeometry(kwargs["geometry"])
            label.setText(kwargs["text"])
            return label
        elif object_type == QPushButton:
            # create QPushButton
            button = QPushButton(window)
            button.setText(kwargs["text"])
            button.setToolTip(kwargs["tooltip"])
            button.move(kwargs["position"][0], kwargs["position"][1])
            button.setFixedHeight(22)
            button.clicked.connect(kwargs["func"])
            return button
        elif object_type == QLineEdit:
            # create QLineEdit
            line_edit = QLineEdit(window)
            line_edit.setText(str(kwargs["text"]))
            line_edit.move(kwargs["position"][0], kwargs["position"][1])
            line_edit.setFixedWidth(30)
            if "validator" in kwargs:
                if kwargs["validator"] == "int":
                    validator = QIntValidator()
                elif kwargs["validator"] == "float":
                    validator = QDoubleValidator()
                line_edit.setValidator(validator)
            line_edit.editingFinished.connect(kwargs["func"])
            return line_edit
