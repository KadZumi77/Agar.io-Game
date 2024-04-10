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

        self.errors = 0

        self.speed_x = 5
        self.speed_y = 2

    def change_speed(self, v):
        pass

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
            player.change_speed(data)
        except:
            pass
        player.update()

    # отправляем новое состояние игрового поля
    for player in players:
        try:
            player.connection.send('Новое состояние игры'.encode())
            player.errors = 0
        except:
            player.errors += 1
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
