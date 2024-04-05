import socket
import pygame

#подключаемся к серверу
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
sock.connect(('localhost', 10000))

#создание окна игры
pygame.init()
screen=pygame.display.set_mode((800,700))
pygame.display.set_caption(' Agar.io')

while True:
    # считываем команду

    # отправляем команду на сервер
    sock.send('Хочу идти вправо'.encode())

    # получаем от сервера новое состояние игрового поля
    data = sock.recv(1024)
    data = data.decode()

    # рисуем новое состояние игрового поля
    print(data)
