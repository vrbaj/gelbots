"""
Implements Factory pattern for Qt graphical object creation.
"""
from PyQt5.QtWidgets import QLabel, QPushButton, QLineEdit


class QtFactory:
    @staticmethod
    def get_object(object_type, window, **kwargs):
        if object_type == QLabel:
            # create QLabel
            label = QLabel(window)
            label.setGeometry(kwargs["geometry"])
            label.setText(kwargs["text"])
            return label
        elif object_type == QPushButton:
            # create QPush Button
            button = QPushButton(window)
            button.setText(kwargs["text"])
            button.setToolTip(kwargs["tooltip"])
            button.move(kwargs["position"][0], kwargs["position"][1])
            button.setFixedHeight(22)
            button.clicked.connect(kwargs["func"])
            return button
        elif object_type == QLineEdit:
            line_edit = QLineEdit
            return line_edit
