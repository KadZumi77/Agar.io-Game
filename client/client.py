import socket
import pygame

WIDTH_WINDOW, HEIGHT_WINDOW = 1500, 900
colors = {'0': (255, 255, 0), '1': (255, 0, 0), '2': (0, 255, 0), '3': (0, 0, 255), '4': (128, 0, 128)}


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


def draw_opponents(data):
    for i in range(len(data)):
        j = data[i].split(' ')

        x = WIDTH_WINDOW // 2 + int(j[0])
        y = HEIGHT_WINDOW // 2 + int(j[1])
        r = int(j[2])
        c = colors[j[3]]
        pygame.draw.circle(screen, c, (x, y), r)

class Me():
    def __init__(self, data):
        data = data.split()
        self.r = int(data[0])
        self.colour = data[1]

    def update(self, new_r):
        self.r = new_r

    def draw(self):
        if self.r != 0:
            pygame.draw.circle(screen, colors[self.colour],
                               (WIDTH_WINDOW // 2, HEIGHT_WINDOW // 2), self.r)

            #write_name(WIDTH_WINDOW // 2, HEIGHT_WINDOW // 2, self.r, my_name)



# подключаемся к серверу
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
sock.connect(('localhost', 10000))

data = sock.recv(64).decode()
me=Me(data)

# создание окна игры
pygame.init()
screen = pygame.display.set_mode((WIDTH_WINDOW, HEIGHT_WINDOW))
pygame.display.set_caption(' Agar.io')

old_v = (0, 0)
v = (0, 0)
running = True
while running:
    # считываем команду
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # считаем положение мыши
    if pygame.mouse.get_focused():
        pos = pygame.mouse.get_pos()
        v = (pos[0] - WIDTH_WINDOW // 2, pos[1] - HEIGHT_WINDOW // 2)
        if v[0] ** 2 + (v[1]) ** 2 <= me.r ** 2:  # когда курсор на бактерии
            v = (0, 0)

    # отправляем вектор направления, если поменялся
    if v != old_v:
        old_v = v
        message = '<' + str(v[0]) + ',' + str(v[1]) + '>'
        sock.send(message.encode())

    # получаем от сервера новое состояние игрового поля
    try:
        data = sock.recv(2 ** 20)
    except:
        running = False
        continue
    # data = sock.recv(2 ** 20)
    data = data.decode()
    data = find(data)
    data = data.split(',')

    # рисуем новое состояние игрового поля
    screen.fill('gray25')

    if data != ['']:
        me.update(int(data[0]))
        draw_opponents(data[1:])
        me.draw()

    #pygame.draw.circle(screen, colors[my_color], (WIDTH_WINDOW // 2, HEIGHT_WINDOW // 2), my_r)
    pygame.display.update()
pygame.quit()
