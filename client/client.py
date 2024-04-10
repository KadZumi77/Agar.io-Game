import socket
import pygame

WIDTH_WINDOW,HEIGHT_WINDOW=800,700
#подключаемся к серверу
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
sock.connect(('localhost', 10000))

#создание окна игры
pygame.init()
screen=pygame.display.set_mode((WIDTH_WINDOW,HEIGHT_WINDOW))
pygame.display.set_caption(' Agar.io')

old_v=(0,0)
running=True
while running:
    # считываем команду
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running=False

    #считаем положение мыши
    if pygame.mouse.get_focused():
        pos=pygame.mouse.get_pos()
        v=(pos[0]-WIDTH_WINDOW//2,pos[1]-HEIGHT_WINDOW//2)
        if v[0]**2+(v[1])**2<=50**2:   #когда курсор на бактерии
            v=(0,0)


    # отправляем вектор направления, если поменялся
    if v!=old_v:
        old_v=v
        message='<'+str(v[0])+','+str(v[1])+'>'
        sock.send(message.encode())

    # получаем от сервера новое состояние игрового поля
    data = sock.recv(2**20)
    data = data.decode()

    # рисуем новое состояние игрового поля
    screen.fill('gray25')
    pygame.draw.circle(screen,(255,0,0),(WIDTH_WINDOW//2,HEIGHT_WINDOW//2),50)
    pygame.display.update()
pygame.quit()