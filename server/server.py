import socket
import time
import pygame
import random

WIDTH_ROOM, HEIGHT_ROOM = 4000, 4000
WIDTH_SERVER_WINDOW, HEIGHT_SERVER_WINDOW = 300, 300
FPS = 100
START_PLAYER_SIZE = 50
colors = {'0': (255, 255, 0), '1': (255, 0, 0), '2': (0, 255, 0), '3': (0, 0, 255), '4': (128, 0, 128)}


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


class Player():
    def __init__(self, connection, addres, x, y, r, color):
        self.connection = connection
        self.addres = addres
        self.x = x
        self.y = y
        self.r = r
        self.color = color

        self.w_vision = 800
        self.h_vision = 700
        self.errors = 0

        self.abs_speed = 3
        self.speed_x = 0
        self.speed_y = 0

    def change_speed(self, v):
        if (v[0] == 0) and (x[1] == 0):
            self.speed_x = 0
            self.speed_y = 0
        else:
            lenv = (v[0] ** 2 + v[1] ** 2) ** 0.5
            v = (v[0] / lenv, v[1] / lenv)
            v = (v[0] * self.abs_speed, v[1] * self.abs_speed)
            self.speed_x, self.speed_y = v[0], v[1]

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y


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
players = []
server_works = True

while server_works:
    clock.tick(FPS)
    # проверяем, есть ли желающие войти в игру
    try:
        new_socket, addres = main_socket.accept()
        print('Подключился', addres)
        new_socket.setblocking(0)
        new_player = Player(new_socket, addres,
                            random.randint(0, WIDTH_ROOM),
                            random.randint(0, HEIGHT_ROOM),
                            START_PLAYER_SIZE, str(random.randint(0, 4)))
        new_player.connection.send(new_player.color.encode())
        players.append(new_player)
    except:
        # print('Нет желающих войти в игру')
        pass

    # считываем команды игроков
    for player in players:
        try:
            data = player.connection.recv(1024)
            data = data.decode()
            data = find(data)
            # обрабатываем команды
            player.change_speed(data)
        except:
            pass
        player.update()

    # определим, что видит каждыцй игрок
    visible_balls = [[] for i in range(len(players))]
    for i in range(len(players)):
        for j in range(i + 1, len(players)):
            # рассматриваем пару i и j игрока
            dist_x = players[j].x - players[i].x
            dist_y = players[j].y - players[i].y

            # i видит j
            if ((abs(dist_x) <= (players[i].w_vision) // 2 + players[j].r)
                    and (abs(dist_y) <= (players[i].h_vision) // 2 + players[j].r)):
                # подготовим данные к добавлению в список видимых шаров
                x_ = str(round(dist_x))
                y_ = str(round(dist_y))
                r_ = str(round(players[j].r))
                c_ = players[j].color

                visible_balls[i].append(x_ + ' ' + y_ + ' ' + r_ + ' ' + c_)

            #j видит i
            if ((abs(dist_x) <= (players[j].w_vision) // 2 + players[i].r)
                    and (abs(dist_y) <= (players[j].h_vision) // 2 + players[i].r)):
                # подготовим данные к добавлению в список видимых шаров
                x_ = str(round(-dist_x))
                y_ = str(round(-dist_y))
                r_ = str(round(players[i].r))
                c_ = players[i].color

                visible_balls[j].append(x_ + ' ' + y_ + ' ' + r_ + ' ' + c_)

    #формируем ответ каждому игроку
    otvets=['' for i in range(len(players))]
    for i in range(len(players)):
        otvets[i]='<'+(','.join(visible_balls[i]))+'>'

    # отправляем новое состояние игрового поля
    for i in range(len(players)):
        try:
            players[i].connection.send(otvets[i].encode())
            players[i].errors = 0
        except:
            players[i].errors += 1
            # print('Отключился игрок')
    # time.sleep(0.01)

    # чистим сервер от затупивших игроков
    for player in players:
        if player.errors == 500:
            player.connection.close()
            players.remove(player)

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
