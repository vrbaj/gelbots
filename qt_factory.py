"""
Implements Factory pattern for Qt graphical object creation.
"""
from PyQt5.QtWidgets import QLabel, QPushButton, QLineEdit
from PyQt5.QtGui import QIntValidator, QDoubleValidator


class QtFactory:
    """
    Factory for PyQt5 objects that are added to windows.
    """
    # TODO replace label, button etc by general object_like and add single return statement?

    @staticmethod
    def get_object(object_type, window, **kwargs):
        qt_object = None
        if object_type == QLabel:
            # create QLabel
            qt_object = QLabel(window)
            qt_object.setGeometry(kwargs["geometry"])
            qt_object.setText(kwargs["text"])
        elif object_type == QPushButton:
            # create QPushButton
            qt_object = QPushButton(window)
            qt_object.setText(kwargs["text"])
            qt_object.setToolTip(kwargs["tooltip"])
            qt_object.move(kwargs["position"][0], kwargs["position"][1])
            qt_object.setFixedHeight(22)
            qt_object.clicked.connect(kwargs["func"])
        elif object_type == QLineEdit:
            # create QLineEdit
            qt_object = QLineEdit(window)
            qt_object.setText(str(kwargs["text"]).replace(".", ","))
            qt_object.move(kwargs["position"][0], kwargs["position"][1])
            qt_object.setFixedWidth(30)
            if "validator" in kwargs:
                if kwargs["validator"] == "int":
                    validator = QIntValidator()
                elif kwargs["validator"] == "float":
                    validator = QDoubleValidator()
                qt_object.setValidator(validator)
            qt_object.editingFinished.connect(kwargs["func"])
        return qt_object
