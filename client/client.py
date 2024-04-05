import socket

sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1)
sock.connect(('localhost',10000))

while True:
    #считываем команду

    #отправляем команду на сервер
    sock.send('Хочу идти вправо'.encode())

    #получаем от сервера новое состояние игрового поля
    data=sock.recv(1024)
    data=data.decode()

    #рисуем новое состояние игрового поля
    print(data)