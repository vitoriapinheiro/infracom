import socket
import threading
import queue
import os
import time
# from colorama import Fore, Back, Style
import datetime

messages = queue.Queue()
clients = []

num_seq_list = []     # número de sequencia inicial

expected_num_seq = [] # primeiro número de sequencia esperado

acks = []

time = 180            # tempo em segundos para poder banir um usuário
timer = []            # ultimo momento que o usuário baniu alguem

clients_names = []
ban_counter = []
banned_names = []     # lista de usuários banidos
vote_checker = False
ban_checker = False

BUFFER_SIZE = 1024

flag = 0

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(('localhost', 9999))

# def timeChecker():
#     global timer, clients, ban_counter, banned_names, ban_checker, vote_checker
#     currTime = datetime.datetime.now()
#     print("current time: ", currTime)

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
          name = message.decode().split(':')[0]
          if name not in banned_names:
            messages.put((message, address))
        except:
          pass

def broadcast():
    global num_seq_list, acks, clients
    global expected_num_seq
    global vote_checker, ban_checker
    banned_index = -1
    while True:
      while not messages.empty():
        date_time = datetime.datetime.now()
        local_time = date_time.strftime("%X")
        message, address = messages.get()
        ack = message[0]
        
        message = message[1:]
        name = message.decode().split(':')[0]
        print("name", name)
        print(message.decode())
        print("banneds", banned_names)
        if address not in clients and name not in banned_names:
          clients.append(address)
          num_seq_list.append(b'0')
          expected_num_seq.append(b'1')
        if name not in banned_names:
          send_ACK(ack, address)               # ACK for received message
        
        for i, client in enumerate(clients):
          if message.decode().startswith('hi, meu nome eh:'):
            name = message.decode().split(':')[1]
            
            if (name in banned_names):
              send_pkt(f'[{local_time}] O usuario {name} esta banido, nao pode entrar'.encode(), client, i)
              if clients[i] == address:       # se o usuario que tentou entrar estive banido
                clients.pop(i)
                num_seq_list.pop(i)
                expected_num_seq.pop(i)

            else:
              if i == 0:                # only append once
                clients_names.append(name)
                ban_counter.append([])
              send_pkt(f'[{local_time}]hi, meu nome eh:{name}'.encode(), client, i)
          else:
            message_content = message.decode().split(':')[1]
            name_request = message.decode().split(':')[0]
            if name_request in banned_names:
              send_pkt(f'[{local_time}] Você esta banido, nao pode enviar mensagens'.encode(), address, 1)

            else:
              if message_content == " bye":
                send_pkt(f'[{local_time}] {name_request} saiu do chat! :('.encode(), client, i)

              elif message_content == " list":
                if name_request == clients_names[i]:
                  send_pkt(f'[{local_time}] {clients_names}'.encode(), client, i)

              elif (message_content.strip()).startswith(f'@{clients_names[i]}'):
                send_pkt(message_content.encode(), client, i)

              elif (message_content.strip()).startswith('ban @') and name_request not in ban_counter[i]: # Verifica se o usuário que está banindo não está na lista de banidos
                if (message_content.strip()).startswith(f'ban @{clients_names[i]}'):
                  ban_counter[i].append(name_request)
                  print("ban counter:", ban_counter)
                  if len(ban_counter[i]) >= 2*len(clients_names)/3:
                    ban_checker = True
                    banned_index = i
                    
                  vote_checker = True

                if vote_checker:
                  send_pkt(f'[{local_time}] {len(ban_counter[i])}/{len(clients_names)} - ban {clients_names[i]}'.encode(), client, i)
                  vote_checker = False
                  
                if ban_checker:
                  send_pkt(f'[{local_time}] O usuario {clients_names[i]} foi banido!!!'.encode(), client, i)
                  ban_checker = False

              elif not (message_content.strip()).startswith(f'@'):
                send_pkt(f'[{local_time}] {message.decode()}'.encode(), client, i)

          if message.decode().split(':')[1] == " bye":
            index = clients_names.index(name_request)
            clients.pop(index)
            clients_names.pop(index)
            ban_counter.pop(index)
            num_seq_list.pop(index)
            expected_num_seq.pop(index)

          if len(ban_counter[banned_index]) >= 2*len(clients_names)/3:
            banned_names.append(clients_names[banned_index])
            clients.pop(banned_index)
            clients_names.pop(banned_index)
            ban_counter.pop(banned_index)
            num_seq_list.pop(banned_index)
            expected_num_seq.pop(banned_index)
            banned_index = 0


t1 = threading.Thread(target=receive_message)
t2 = threading.Thread(target=broadcast)

t1.start()
t2.start()
