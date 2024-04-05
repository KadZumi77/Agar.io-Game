import socket
import time

main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
main_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
main_socket.bind(('localhost', 10000))
main_socket.setblocking(0)
main_socket.listen(5)
print('Создался сокет')
players_sockets=[]

while True:
    #проверяем, есть ли желающие войти в игру
    try:
        new_socket,addr=main_socket.accept()
        print('Подключился',addr)
        new_socket.setblocking(0)
        players_sockets.append(new_socket)
    except:
        print('Нет желающих войти в игру')
        pass

    #считываем команды игроков

    #отправляем новое состояние игрового поля
    time.sleep(1)


