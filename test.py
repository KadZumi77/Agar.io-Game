from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QLabel, QApplication, QPushButton, QVBoxLayout, QDialog, QLineEdit, QTextEdit
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget
import sys


class Main(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setMinimumSize(450, 200)
        self.setFocus()

        self.setWindowTitle("WELCOME")
        layout = QVBoxLayout()
        self.setLayout(layout)
        lose_label = QLabel("Введите свой никнейм:")

        lose_label.setFont(QFont('Arial', 20))
        layout.addWidget(lose_label)
        lineEdit = QLineEdit(self)
        font = lineEdit.font()  # lineedit current font
        font.setPointSize(28)  # change it's size
        lineEdit.setFont(font)
        layout.addWidget(lineEdit)
        ok_button = QPushButton("Продолжить")
        layout.addWidget(ok_button)
        ok_button.clicked.connect(self.close)
        #name_dialog.destroy()
        #name_dialog.exec_()
        #sys.exit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    application = Main()
    application.show()

    sys.exit(app.exec_())