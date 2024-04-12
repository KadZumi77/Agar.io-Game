import socket
import time
import pygame
import random

WIDTH_ROOM, HEIGHT_ROOM = 4000, 4000
WIDTH_SERVER_WINDOW, HEIGHT_SERVER_WINDOW = 300, 300
FPS = 100
START_PLAYER_SIZE = 50

MOBS_QUANTITY = 25
MICROBE_SIZE = 15
MICROBES_QUANTITY = (WIDTH_ROOM * HEIGHT_ROOM) // 60000

colors = {'0': (255, 255, 0), '1': (255, 0, 0), '2': (0, 255, 0), '3': (0, 0, 255), '4': (128, 0, 128)}

v = (0, 0)


def new_r(R, r):
    return (R ** 2 + r ** 2) ** 0.5


def find(s):
    otkr = None
    for i in range(len(s)):
        if s[i] == '<':
            otkr = i
        if s[i] == '>' and otkr != None:
            zakr = i
            res = s[otkr + 1:zakr]
            res = list(map(int, res.split(',')))
            return res
    return ''


class Microbe():
    def __init__(self, x, y, r, color):
        self.x = x
        self.y = y
        self.r = r
        self.color = color


class Player():
    def __init__(self, connection, addres, x, y, r, color):
        self.connection = connection
        self.addres = addres
        self.x = x
        self.y = y
        self.r = r
        self.color = color
        self.L = 1

        self.width_window = 900
        self.height_window = 800
        self.w_vision = 900
        self.h_vision = 800
        self.errors = 0

        self.abs_speed = 30 / (self.r ** 0.5)
        self.speed_x = 0
        self.speed_y = 0

    def change_speed(self, v):
        if (v[0] == 0) and (v[1] == 0):
            self.speed_x = 0
            self.speed_y = 0
        else:
            lenv = (v[0] ** 2 + v[1] ** 2) ** 0.5
            v = (v[0] / lenv, v[1] / lenv)
            v = (v[0] * self.abs_speed, v[1] * self.abs_speed)
            self.speed_x, self.speed_y = v[0], v[1]

    def update(self):
        # x coordinate
        if self.x - self.r <= 0:
            if self.speed_x >= 0:
                self.x += self.speed_x
        else:
            if self.x + self.r >= WIDTH_ROOM:
                if self.speed_x <= 0:
                    self.x += self.speed_x
            else:
                self.x += self.speed_x

        # y coordinate
        if self.y - self.r <= 0:
            if self.speed_y >= 0:
                self.y += self.speed_y
        else:
            if self.y + self.r >= HEIGHT_ROOM:
                if self.speed_y <= 0:
                    self.y += self.speed_y
            else:
                self.y += self.speed_y

        # abs_speed
        if self.r != 0:
            self.abs_speed = 20 / (self.r ** 0.5)
        else:
            self.abs_speed = 0

        # r
        if self.r >= 100:
            self.r -= self.r / 18000

        # L
        if (self.r >= self.w_vision / 4) or (self.r >= self.h_vision / 4):
            if (self.w_vision <= WIDTH_ROOM) or (self.h_vision <= HEIGHT_ROOM):
                self.L *= 2
                self.w_vision = self.width_window * self.L
                self.h_vision = self.height_window * self.L
        if (self.r < self.w_vision / 8) and (self.r < self.h_vision / 8):
            if self.L > 1:
                self.L = self.L // 2
                self.w_vision = self.width_window * self.L
                self.h_vision = self.height_window * self.L


# создание сокета
main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
main_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
main_socket.bind(('localhost', 10000))
main_socket.setblocking(0)
main_socket.listen(5)

# создание графического окна сервера
pygame.init()
screen = pygame.display.set_mode((WIDTH_SERVER_WINDOW, HEIGHT_SERVER_WINDOW))
clock = pygame.time.Clock()

# создание набора мобов
players = [Player(None, None,
                  random.randint(0, WIDTH_ROOM),
                  random.randint(0, HEIGHT_ROOM),
                  random.randint(10, 100),
                  str(random.randint(0, 4)))
           for i in range(MOBS_QUANTITY)]
# создание набора микробов
microbes = [Microbe(random.randint(0, WIDTH_ROOM),
                    random.randint(0, HEIGHT_ROOM),
                    MICROBE_SIZE,
                    str(random.randint(0, 4)))
            for i in range(MICROBES_QUANTITY)]

tick = -1
server_works = True
while server_works:
    tick += 1
    clock.tick(FPS)
    if tick == 150:
        tick = 0
        # проверяем, есть ли желающие войти в игру
        try:
            new_socket, addres = main_socket.accept()
            print('Подключился', addres)
            new_socket.setblocking(0)
            new_player = Player(new_socket, addres,
                                random.randint(0, WIDTH_ROOM),
                                random.randint(0, HEIGHT_ROOM),
                                START_PLAYER_SIZE, str(random.randint(0, 4)))
            message = str(new_player.r) + ' ' + new_player.color
            new_player.connection.send(message.encode())
            players.append(new_player)
        except:
            # print('Нет желающих войти в игру')
            pass
        # дополняем список мобов
        for i in range(MOBS_QUANTITY - len(players)):
            if len(microbes) != 0:
                spawn = random.choice(microbes)
                players.append(Player(None, None,
                                      spawn.x,
                                      spawn.y,
                                      random.randint(10, 100),
                                      str(random.randint(0, 4))
                                      )
                               )
                microbes.remove(spawn)

        # дополняем список микробов
        new_microbes = [Microbe(random.randint(0, WIDTH_ROOM),
                                random.randint(0, HEIGHT_ROOM),
                                MICROBE_SIZE,
                                str(random.randint(0, 4)))
                        for i in range(MICROBES_QUANTITY - len(microbes))
                        ]

        microbes = microbes + new_microbes

    # считываем команды игроков
    for player in players:
        if player.connection != None:
            try:
                data = player.connection.recv(1024)
                data = data.decode()
                data = find(data)
                # обрабатываем команды
                player.change_speed(data)
            except:
                pass

        else:
            if tick == 100:
                data = [random.randint(-100, 100), random.randint(-100, 100)]
                player.change_speed(data)
        player.update()

    # определим, что видит каждыцй игрок
    visible_balls = [[] for i in range(len(players))]
    for i in range(len(players)):
        # каких микробов видит i игрок
        for k in range(len(microbes)):
            dist_x = microbes[k].x - players[i].x
            dist_y = microbes[k].y - players[i].y

            # i видит k
            if ((abs(dist_x) <= (players[i].w_vision) // 2 + microbes[k].r)
                    and
                    (abs(dist_y) <= (players[i].h_vision) // 2 + microbes[k].r)):
                # i может съесть k
                if (dist_x ** 2 + dist_y ** 2) ** 0.5 <= players[i].r:
                    players[i].r = new_r(players[i].r, microbes[k].r)
                    microbes[k].r = 0

                if (players[i].connection != None) and (microbes[k].r != 0):
                    # подготовим данные к добавлению в список видимых шаров
                    x_ = str(round(dist_x / players[i].L))
                    y_ = str(round(dist_y / players[i].L))
                    r_ = str(round(microbes[k].r / players[i].L))
                    c_ = microbes[k].color

                    visible_balls[i].append(x_ + ' ' + y_ + ' ' + r_ + ' ' + c_)

        for j in range(i + 1, len(players)):
            # рассматриваем пару i и j игрока
            dist_x = players[j].x - players[i].x
            dist_y = players[j].y - players[i].y

            # i видит j
            if ((abs(dist_x) <= (players[i].w_vision) // 2 + players[j].r)
                    and (abs(dist_y) <= (players[i].h_vision) // 2 + players[j].r)):

                # i может съесть j
                if ((dist_x ** 2 + dist_y ** 2) ** 0.5 <= players[i].r and
                        players[i].r > 1.1 * players[j].r):
                    players[i].r = new_r(players[i].r, players[j].r)
                    players[j].r, players[j].speed_x, players[j].speed_y = 0, 0, 0  # изменим радиус i игрока

                if players[i].connection != None:
                    # подготовим данные к добавлению в список видимых шаров
                    x_ = str(round(dist_x / players[i].L))
                    y_ = str(round(dist_y / players[i].L))
                    r_ = str(round(players[j].r / players[i].L))
                    c_ = players[j].color

                    visible_balls[i].append(x_ + ' ' + y_ + ' ' + r_ + ' ' + c_)

            # j видит i
            if ((abs(dist_x) <= (players[j].w_vision) // 2 + players[i].r)
                    and (abs(dist_y) <= (players[j].h_vision) // 2 + players[i].r)):
                # j может съесть i
                if ((dist_x ** 2 + dist_y ** 2) ** 0.5 <= players[j].r and
                        players[j].r > 1.1 * players[i].r):
                    players[j].r = new_r(players[j].r, players[i].r)
                    players[i].r, players[i].speed_x, players[i].speed_y = 0, 0, 0  # изменим радиус j игрока

                if players[j].connection != None:
                    # подготовим данные к добавлению в список видимых шаров
                    x_ = str(round(-dist_x / players[j].L))
                    y_ = str(round(-dist_y / players[j].L))
                    r_ = str(round(players[i].r / players[j].L))
                    c_ = players[i].color

                    visible_balls[j].append(x_ + ' ' + y_ + ' ' + r_ + ' ' + c_)

    # формируем ответ каждому игроку
    otvets = ['' for i in range(len(players))]
    for i in range(len(players)):
        r_ = str(round(players[i].r))
        # x_ = str(round(players[i].x ))
        # y_ = str(round(players[i].y / players[i].L))
        # L_ = str(players[i].L)

        visible_balls[i] = [r_] + visible_balls[i]
        otvets[i] = '<' + (','.join(visible_balls[i])) + '>'

    # отправляем новое состояние игрового поля
    for i in range(len(players)):
        if players[i].connection != None:
            try:
                players[i].connection.send(otvets[i].encode())
                players[i].errors = 0
            except:
                players[i].errors += 1
                # print('Отключился игрок')
    # time.sleep(0.01)

    # чистим сервер от затупивших игроков
    for player in players:
        if (player.errors == 500) or (player.r == 0):
            if player.connection != None:
                player.connection.close()
            players.remove(player)

    # чистим список от съеденных микробов
    for m in microbes:
        if m.r == 0:
            microbes.remove(m)

    # нарисуем состояние комнаты
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            server_works = False

    screen.fill('black')
    for player in players:
        x = round(player.x * WIDTH_SERVER_WINDOW / WIDTH_ROOM)
        y = round(player.y * HEIGHT_SERVER_WINDOW / HEIGHT_ROOM)
        r = round(player.r * WIDTH_SERVER_WINDOW / WIDTH_ROOM)
        c = colors[player.color]

        pygame.draw.circle(screen, c, (x, y), r)
    pygame.display.update()

pygame.quit()
main_socket.close()
