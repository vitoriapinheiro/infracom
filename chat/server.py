import socket
import threading
import queue
import os
import time
import datetime

messages = queue.Queue()
clients = []          # endereços dos clientes conectados

num_seq_list = []     # número de sequencia inicial

expected_num_seq = [] # primeiro número de sequencia esperado       

timer = 30            # tempo em 30 segundos para poder banir um usuário
ban_timer = []        # ultima  vez que um usuario baniu

clients_names = []    # nome dos usuários conectados
ban_counter = []      # lista de usuários que votaram no banimento de determinado usuário
banned_names = []     # lista de usuários banidos
vote_checker = False
ban_checker = False

BUFFER_SIZE = 1024

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(('localhost', 9999))


# envia ACK correto
def send_ACK(num_seq, client_address):
    global expected_num_seq
    index = clients.index(client_address)

    server.sendto(expected_num_seq[index], client_address) # envia o ACK com o número de sequencia esperado
    
    if num_seq == expected_num_seq[index]:                 # se o que foi recebido era o esperado, muda o número esperado
        expected_num_seq[index] =  b'0' if (expected_num_seq[index] == b'1') else b'1'

# envia pacote para o destino
def send_pkt(msg, address, index):
    global num_seq_list

    num_seq_list[index] = b'0' if (num_seq_list[index] == b'1') else b'1'

    pkt = msg
    server.sendto(pkt, address)                          # enviar o pacote em bytes enquanto tiver

# thread que recebe as mensagens e coloca em uma fila
def receive_message():
    while True:
        try:
          message, address = server.recvfrom(BUFFER_SIZE)
          name = message.decode().split(':')[0]
          if name not in banned_names:
            messages.put((message, address))
        except:
          pass

def broadcast():
    global num_seq_list, clients
    global expected_num_seq
    global vote_checker, ban_checker
    banned_index = -1
    while True:
      while not messages.empty():
        date_time = datetime.datetime.now()
        local_time = date_time.strftime("%X") # tempo atual em HH:MM:SS
        message, address = messages.get()     # pega uma mensagem da fila de mensagens
        ack = message[0]                      # extrai o numero de sequencia da mensagem
        message = message[1:]                 

        name = message.decode().split(':')[0]

        if address not in clients and name not in banned_names:
          clients.append(address)
          num_seq_list.append(b'0')
          expected_num_seq.append(b'1')
          ban_timer.append(0)
        if name not in banned_names:
          send_ACK(ack, address)              # ACK for received message

        in_ban_name = ""
        in_ban_index = 0

        # verifica o index da pessoa que mandou 
        try:
          index_sender = clients.index(address)
        except:
          pass

        ban_checker = False
        vote_checker = False

        # mensagem de verificação de ban
        if (message.decode().split(':')[1].strip()).startswith('ban @'):
          if time.time() >= (ban_timer[index_sender] + timer):          # Verifica se o usuário que está banindo não está na lista de banidos
            in_ban_name = (message.decode().split(':')[1].strip()).split('@')[1]

            for i in range(len(clients)):
              if clients_names[i] == in_ban_name and name not in ban_counter[i]:

                in_ban_index = i
                ban_counter[i].append(name)
                ban_timer[index_sender] = time.time()
                if len(ban_counter[i]) >= 2*len(clients_names)/3:
                  ban_checker = True
                  banned_index = i
                  
                vote_checker = True

        # envio de mensagens para todos os clientes
        for i, client in enumerate(clients):
          # primeira mensagem de um novo cliente
          if message.decode().startswith('hi, meu nome eh:'):
            name = message.decode().split(':')[1]
            
            # se o cliente estiver na lista de banimentos e tenta enviar uma msg, os outros recebem um aviso
            if (name in banned_names):
              send_pkt(f'[{local_time}] O usuario {name} esta banido, nao pode entrar'.encode(), client, i)
              if clients[i] == address:       # se o usuario que tentou entrar estive banido
                clients.pop(i)
                num_seq_list.pop(i)
                expected_num_seq.pop(i)

            # se nao tiver, adiciona o cliente nas listas e envia a mensagem aos usuarios
            else:
              if i == 0:
                clients_names.append(name)
                ban_counter.append([])
              send_pkt(f'[{local_time}]hi, meu nome eh:{name}'.encode(), client, i)
          else:
            message_content = message.decode().split(':')[1]
            name_request = message.decode().split(':')[0]
            # se o nome de quem enviou a mensagem estiver na lista de banimento, ele recebe um aviso
            if name_request in banned_names:
              send_pkt(f'[{local_time}] Você esta banido, nao pode enviar mensagens'.encode(), address, 1)
              break
            
            else:
              # se a mensagem for um bye
              if message_content == " bye":
                send_pkt(f'[{local_time}] {name_request} saiu do chat! :('.encode(), client, i)

              # se o a mensagem for um comando de listagem
              elif message_content == " list":
                if name_request == clients_names[i]:
                  send_pkt(f'[{local_time}] {clients_names}'.encode(), client, i)
              
              # se a mensagem for uma mensagem privada, envia apenas para o destinatário
              elif (message_content.strip()).startswith(f'@{clients_names[i]}'):
                send_pkt(f'[{local_time}] {name_request}:{message_content}'.encode(), client, i)

              # envia mensagem se um voto for adicionado
              if vote_checker:
                send_pkt(f'[{local_time}] {len(ban_counter[in_ban_index])}/{len(clients_names)} - ban {in_ban_name}'.encode(), client, i)
              
              # envia mensagem se um jogador for banido
              if ban_checker:
                send_pkt(f'[{local_time}] O usuario {clients_names[in_ban_index]} foi banido!!!'.encode(), client, i)
              
              # se a mensagem nao for privada, envia para todos
              if not (message_content.strip()).startswith(f'@'):
                send_pkt(f'[{local_time}] {message.decode()}'.encode(), client, i)

        # retira o usuário da lista caso ele seja banido ou saia do chat
        if len(ban_counter[banned_index]) >= 2*len(clients_names)/3:
          banned_names.append(clients_names[banned_index])
          clients.pop(banned_index)
          clients_names.pop(banned_index)
          ban_counter.pop(banned_index)
          num_seq_list.pop(banned_index)
          expected_num_seq.pop(banned_index)
          ban_timer.pop(banned_index)
          banned_index = 0

        # retira o usuário da lista caso ele saia do chat
        if message.decode().split(':')[1] == " bye":
          index = clients_names.index(name_request)
          clients.pop(index)
          clients_names.pop(index)
          ban_counter.pop(index)
          num_seq_list.pop(index)
          expected_num_seq.pop(index)
          ban_timer.pop(index)

t1 = threading.Thread(target=receive_message)
t2 = threading.Thread(target=broadcast)

t1.start()
t2.start()
