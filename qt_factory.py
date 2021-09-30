from PyQt5.QtWidgets import QLabel, QPushButton


class QtFactory:
    @staticmethod
    def get_object(object_type, window, **kwargs):
        if object_type == QLabel:
            # create QLabel
            label = QLabel(window)
            label.setGeometry(kwargs["geometry"])
            label.setText(kwargs["text"])
            return label
        if object_type == QPushButton:
            # create QPush Button
            pass
