import socket
import threading
import queue

messages = queue.Queue()
clients = []

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(('localhost', 9999))

def receive_message():
    while True:
      try:
        message, address = server.recvfrom(1024)
        messages.put((message, address))
      except:
        pass

def broadcast():
    while True:
      while not messages.empty():
        message, address = messages.get()
        print(message.decode())
        if address not in clients:
          clients.append(address)
        for client in clients:
          try:
            if message.decode().startswith('NOME:'):
              name = message.decode().split(':')[1]
              server.sendto(f'{name} entrou no chat'.encode(), client)
            else:
              server.sendto(message, client)
          except:
            clients.remove(client)
            
t1 = threading.Thread(target=receive_message)
t2 = threading.Thread(target=broadcast)

t1.start()
t2.start()
