import socket
import pygame
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QPushButton, QVBoxLayout, QLabel, QWidget, QLineEdit
import sys

class HelloWindow(QWidget):
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
        font = self.lineEdit.font()
        font.setPointSize(28)
        self.lineEdit.setFont(font)
        layout.addWidget(self.lineEdit)
        self.ok_button = QPushButton("Продолжить")
        layout.addWidget(self.ok_button)
        self.ok_button.clicked.connect(self.showLine)

    def showLine(self):
        self.my_name = self.lineEdit.text()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    application = HelloWindow()
    application.show()
    app.exec_()

my_name = application.my_name
server_ip = 'localhost'
# server_ip = '123.123.123.123'

WIDTH_WINDOW, HEIGHT_WINDOW = 1200, 900
colours = {'0': (255, 255, 0), '1': (255, 0, 0), '2': (0, 255, 0), '3': (0, 255, 255), '4': (128, 0, 128)}
# my_name = 'Diana'
GRID_COLOUR = (150, 150, 150)

def find(s):
    otkr = None
    for i in range(len(s)):
        if s[i] == '<':
            otkr = i
        if s[i] == '>' and otkr != None:
            zakr = i
            res = s[otkr + 1:zakr]
            return res
    return ''

def write_name(x, y, r, name):
    font = pygame.font.Font(None, r)
    text = font.render(name, True, (0, 0, 0))
    rect = text.get_rect(center=(x, y))
    screen.blit(text, rect)

def draw_opponents(data):
    for i in range(len(data)):
        j = data[i].split(' ')

        x = WIDTH_WINDOW // 2 + int(j[0])
        y = HEIGHT_WINDOW // 2 + int(j[1])
        r = int(j[2])
        c = colours[j[3]]
        pygame.draw.circle(screen, c, (x, y), r)

        if len(j) == 5: write_name(x, y, r, j[4])

class Me():
    def __init__(self, data):
        data = data.split()
        self.r = int(data[0])
        self.colour = data[1]

    def update(self, new_r):
        self.r = new_r

    def draw(self):
        if self.r != 0:
            pygame.draw.circle(screen, colours[self.colour],
                               (WIDTH_WINDOW // 2, HEIGHT_WINDOW // 2), self.r)

            write_name(WIDTH_WINDOW // 2, HEIGHT_WINDOW // 2, self.r - 20, str(my_name))

class Grid():
    def __init__(self, screen):
        self.screen = screen
        self.x = 500
        self.y = 500
        self.start_size = 200
        self.size = self.start_size

    def update(self, cur_x, cur_y, L):
        self.size = self.start_size // L
        self.x = -self.size + (-cur_x) % (self.size)
        self.y = -self.size + (-cur_y) % (self.size)

    def draw(self):
        for i in range(WIDTH_WINDOW // self.size + 2):
            pygame.draw.line(self.screen, GRID_COLOUR,
                             [self.x + i * self.size, 0],  # координаты верхнего конца отрезка
                             [self.x + i * self.size, HEIGHT_WINDOW],  # координаты нижнего конца отрезка
                             1)

        for i in range(HEIGHT_WINDOW // self.size + 2):
            pygame.draw.line(self.screen, GRID_COLOUR,
                             [0, self.y + i * self.size],
                             [WIDTH_WINDOW, self.y + i * self.size],
                             1)

v = (0, 0)
old_v = (0, 0)

class WindowLose(QWidget):
    def __init__(self):
        super().__init__()


        self.setMinimumSize(200, 100)
        self.setFocus()
        self.setWindowTitle("Losing")
        layout = QVBoxLayout()
        self.setLayout(layout)
        lose_label = QLabel("Ой-ой, кажется тебя съели(")
        lose_label.setFont(QFont('Arial', 20))
        layout.addWidget(lose_label)
        self.ok_button = QPushButton("Выход")
        self.ok_button.setFont(QFont('Arial', 10))
        self.ok_button.clicked.connect(self.closeGame)
        layout.addWidget(self.ok_button)
        #sys.exit()
        # self.restart_button = QPushButton("Переиграть")
        # self.restart_button.setFont(QFont('Arial', 10))
        # self.restart_button.clicked.connect(self.restart_button)
        # layout.addWidget(self.restart_button)
    def closeGame(self):
        self.close()
        sys.exit()

# создание окна игры
pygame.init()
screen = pygame.display.set_mode((WIDTH_WINDOW, HEIGHT_WINDOW))

class Game():
    # подключение к серверу
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    sock.connect((server_ip, 10000))

    # отправляем серверу свой ник и размеры окна
    sock.send(('.' + str(my_name) + ' ' + str(WIDTH_WINDOW) + ' ' + str(HEIGHT_WINDOW) + '.').encode())

    # получаем свой размер и цвет
    data = sock.recv(64).decode()

    # подтверждаем получение
    sock.send('!'.encode())

    pygame.display.set_caption(' Agar.io')
    me = Me(data)
    grid = Grid(screen)

    running = True

    while running:
        # обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        # считаем положение мыши игрока
        if pygame.mouse.get_focused():
            pos = pygame.mouse.get_pos()
            v = (pos[0] - WIDTH_WINDOW // 2, pos[1] - HEIGHT_WINDOW // 2)

            if (v[0]) ** 2 + (v[1]) ** 2 <= me.r ** 2:
                v = (0, 0)

        # отправляем вектор желаемого направления движения,
        # если он поменялся
        if v != old_v:
            old_v = v
            message = '<' + str(v[0]) + ',' + str(v[1]) + '>'
            sock.send(message.encode())

        # получение нового состояния игрового поля
        try:
            data = sock.recv(2 ** 20)
        except:
            running = False
            continue
        data = data.decode()
        data = find(data)
        data = data.split(',')

        # обработка сообщения с сервера
        if data != ['']:
            parametrs = list(map(int, data[0].split(' ')))
            me.update(parametrs[0])
            grid.update(parametrs[1], parametrs[2], parametrs[3])

            # Рисуем новое состояние игрового поля
            screen.fill('gray25')
            grid.draw()
            draw_opponents(data[1:])
            me.draw()
        if me.r == 0:
            app = QApplication(sys.argv)
            rules_window = WindowLose()
            rules_window.show()
            app.exec_()
            #sys.exit()

        pygame.display.update()

    pygame.quit()


