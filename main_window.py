import sys
import os
from PyQt6.QtWidgets import (QApplication, QWidget,QDialog,QMainWindow, QLabel, QPushButton, QLineEdit, QButtonGroup, QVBoxLayout,QHBoxLayout,QSpinBox,
                             QCheckBox, QFileDialog)
from PyQt6.QtGui import QFont, QPixmap, QAction, QIcon
from PyQt6.QtCore import Qt
from multy_query import WindowMultyQuery


class MainWindow(QWidget):
    # def __init__(self):
    #     super(WindowMultyQuery, self).__init__()
    #     self.setWindowTitle('Window2')
    def __init__(self):
        super().__init__()

        self.initializeUI()

    def initializeUI(self):
        """Set up the application's GUI."""
        # self.setMaximumSize(310, 130)
        self.setWindowTitle("2GIS_Parcer_by_Sergey_Biryukov")
        self.setUpMainWindow()
        self.show()

    def open_multyquery(self):
        self.hide()
        self.w = WindowMultyQuery()
        self.w.show()
    def open_singlequery(self):
        from single_query import WindowSingleQuery
        self.close()
        self.w = WindowSingleQuery()
        self.w.show()

    def setUpMainWindow(self):
        header_label = QLabel("2GIS_Parcer")
        header_label.setFont(QFont("Arial", 18))
        header_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter)
        question_label = QLabel("Выберете способ выгрузки")
        question_label.setAlignment(Qt.AlignmentFlag.AlignTop)

        button_group = QButtonGroup(self)
        # button_group.buttonClicked.connect(
        #     self.checkboxClicked)



        self.main_v_box = QVBoxLayout()
        self.main_v_box.addWidget(header_label)
        self.main_v_box.addWidget(question_label)

        self.main_h_box = QHBoxLayout()

        self.save_path_textedit = QLineEdit()
        # self.link_url.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.save_path_textedit.setClearButtonEnabled(True)
        # self.link_url.addAction(QIcon('icons/folder_icon.png'), QLineEdit.ActionPosition.LeadingPosition)
        seach_action = self.save_path_textedit.addAction(QIcon('icons/folder_icon.png'),
                                                         QLineEdit.ActionPosition.LeadingPosition)


        self.single_button = QPushButton("По одному элементу")
        button_group.addButton(self.single_button)
        self.single_button.setEnabled(True)
        self.main_v_box.addWidget(self.single_button)



        self.multy_button = QPushButton("Многостраничная выгрузка")
        button_group.addButton(self.multy_button)
        self.multy_button.setEnabled(True)
        self.main_v_box.addWidget(self.multy_button)

        # self.second_button = QPushButton('Многостраничная выгрузка')
        # button_group.addButton(self.second_button)
        # self.main_v_box.addWidget(self.second_button)


        self.setLayout(self.main_v_box)

        self.single_button.clicked.connect(self.open_singlequery)
        # self.link_url.textChanged.connect(self.enabledUrlButt)
        self.multy_button.clicked.connect(self.open_multyquery)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())

