from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QLabel, QApplication, QPushButton, QVBoxLayout, QDialog, QLineEdit, QTextEdit
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget
import sys


class Main(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.my_name = ''

        self.setMinimumSize(450, 200)
        self.setFocus()

        self.setWindowTitle("WELCOME")
        layout = QVBoxLayout()
        self.setLayout(layout)
        name_label = QLabel("Введите свой никнейм:")

        name_label.setFont(QFont('Arial', 20))
        layout.addWidget(name_label)
        self.lineEdit = QLineEdit()
        self.lineEdit.setMaxLength(8)
        font = self.lineEdit.font()  # lineedit current font
        font.setPointSize(28)  # change it's size
        self.lineEdit.setFont(font)
        layout.addWidget(self.lineEdit)
        self.ok_button = QPushButton("Продолжить")
        layout.addWidget(self.ok_button)
        self.ok_button.clicked.connect(self.showLine)
        #name_dialog.destroy()
        #name_dialog.exec_()
        #sys.exit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    application = Main()
    application.show()

    sys.exit(app.exec_())