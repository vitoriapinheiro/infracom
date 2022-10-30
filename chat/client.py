import socket
import threading
import random
# from colorama import Fore, Back, Style

BUFFER_SIZE = 1024 # tamanho do buffer

num_seq = b'0' # número de sequencia inicial

expected_num_seq = b'1' # primeiro número de sequencia esperado

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
SERVER = ('localhost', 9999)

correct_ACK = True

client.bind(('localhost', random.randint(8000, 9000)))

def send_ACK(num_seq, client_address):
    global expected_num_seq

    client.sendto(expected_num_seq, client_address) # envia o ACK com o número de sequencia esperado
    
    if num_seq == expected_num_seq: # se o que foi recebido era o esperado, muda o número esperado
        expected_num_seq =  b'0' if (expected_num_seq == b'1') else b'1'

def send_pkt(msg):
    global num_seq, correct_ACK

    num_seq = b'0' if (num_seq == b'1') else b'1'

    pkt = num_seq + msg
    client.sendto(pkt, SERVER) # enviar o pacote em bytes enquanto tiver
    correct_ACK = False
    while not correct_ACK:
        if socket.timeout:
            break


name = input('Digite seu nome: ')

def receive_message():
    global num_seq, expected_num_seq, correct_ACK
    while True:
        try:
            message, _ = client.recvfrom(BUFFER_SIZE)
            if (message == b'0' or message == b'1'):# se for ACK
                correct_ACK = True
            else:

                print(message.decode())
                # print(Style.RESET_ALL)
        except:
            pass

t = threading.Thread(target=receive_message)
t.start()

send_pkt(f'hi, meu nome eh:{name}'.encode())

while True:
    message = input()
    send_pkt(f'{name}: {message}'.encode())
    if message == 'bye':
        t.join()
        break
