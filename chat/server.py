import socket
import threading
import queue
import os

messages = queue.Queue()
clients = []

num_seq_list = [] # número de sequencia inicial

expected_num_seq = [] # primeiro número de sequencia esperado

acks = []

clients_names = []

BUFFER_SIZE = 1024

flag = 0

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(('localhost', 9999))

def send_ACK(num_seq, client_address):
    global expected_num_seq
    index = clients.index(client_address)

    server.sendto(expected_num_seq[index], client_address) # envia o ACK com o número de sequencia esperado
    
    if num_seq == expected_num_seq[index]: # se o que foi recebido era o esperado, muda o número esperado
        expected_num_seq[index] =  b'0' if (expected_num_seq[index] == b'1') else b'1'

def correct_ACK(index):
    global num_seq

    ACK_msg, _ = server.recvfrom(1) # espera receber o ACK

    if (ACK_msg == num_seq[index]):
        return True
    else:
        return False

def send_pkt(msg, address, index):
    global num_seq_list

    num_seq_list[index] = b'0' if (num_seq_list[index] == b'1') else b'1'

    #while True:
    #pkt = num_seq[index] + msg
    pkt = msg
    server.sendto(pkt, address) # enviar o pacote em bytes enquanto tiver
        # try:
        #     if correct_ACK(index):
        #         break
        # except socket.timeout:
        #     continue

def receive_message():
    global  acks
    while True:
        try:
          message, address = server.recvfrom(BUFFER_SIZE)
          messages.put((message, address))
        except:
          pass

def broadcast():
    global num_seq_list, acks, clients
    global expected_num_seq
    while True:
      while not messages.empty():
        message, address = messages.get()
        ack = message[0]
        message = message[1:]
        print(message.decode())
        if address not in clients:
          clients.append(address)
          num_seq_list.append(b'0')
          expected_num_seq.append(b'1')
        send_ACK(ack, address) # ACK for received message
        
        for i, client in enumerate(clients):
          if message.decode().startswith('hi, meu nome eh:'):
            name = message.decode().split(':')[1]
            if i == 0: # only append once
              clients_names.append(name)
            send_pkt(f'hi, meu nome eh:{name}'.encode(), client, i)
          else:
            message_content = message.decode().split(':')[1]
            name_request = message.decode().split(':')[0]

            if message_content == " bye":
              send_pkt(f'{name_request} saiu do chat! :('.encode(), client, i)

            elif message_content == " list":
              if name_request == clients_names[i]:
                send_pkt(f'{clients_names}'.encode(), client, i)

            else:
              send_pkt(message, client, i)

        if message.decode().split(':')[1] == " bye":
          index = clients_names.index(name_request)
          clients.pop(index)
          clients_names.pop(index)
          num_seq_list.pop(index)
          expected_num_seq.pop(index)
        
            


t1 = threading.Thread(target=receive_message)
t2 = threading.Thread(target=broadcast)

t1.start()
t2.start()
