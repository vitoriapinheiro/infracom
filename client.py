import os
import socket

BUFFER_SIZE = 1024 # tamanho do buffer

SERVER_IP = "localhost" # endereco IP do servidor

SERVER_PORT = 5002 # porta que o servidor esta esperando a msg

SERVER_DEST = (SERVER_IP, SERVER_PORT)

num_seq = b'0'

def correct_ACK():
    global num_seq

    ACK_msg, _ = udp.recvfrom(1) # espera receber o ACK
    if (ACK_msg == num_seq):
        print(f'ok: recebido ({ACK_msg})')
        return True
    else:
        print(f'ack errado: esperado ({num_seq}), recebido ({ACK_msg})')
        return False

def send_pkt(msg):
    global num_seq

    num_seq = b'0' if (num_seq == b'1') else b'1'

    while True:
        pkt = num_seq + msg
        udp.sendto(pkt, SERVER_DEST) # enviar o pacote em bytes enquanto tiver
        print(f"enviou pacote {num_seq}")
        if correct_ACK():
            break

udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # criando o socket udp

files = []

# Enviando arquivos

# Leitura de todos os arquivos da pasta
directory = 'origin'
for i, filename in enumerate(os.listdir(directory)): 
    f = os.path.join(directory, filename) 
    
    if os.path.isfile(f): 
        print(filename)
        files.append(filename)

os.chdir(directory) 

for file in files:
    filename_encoded = bytes(file, "utf-8") # codificar o nome do arquivo
    send_pkt(filename_encoded)
    
    with open(file, "rb") as f:
        while True:
            bytes_read = f.read(BUFFER_SIZE-1) # ler o arquivo
            if not bytes_read:
                print(f"arquivo '{file}' enviado") 
                send_pkt(b"ENDFILE")
                break
            else: # envia pacote
                send_pkt(bytes_read)

        f.close()

print("Todos os arquivos foram enviados")

send_pkt(b"END")


# os.chdir("../")

# directory = "destiny"

# try:
#     os.mkdir(directory) # cria o diretório e entra nele
# except: 
#     pass

# os.chdir(directory)


# # Recebendo arquivos
# while True:
#     filename, server_address = udp.recvfrom(BUFFER_SIZE) # recebe o nome do arquivo
#     filename = filename.decode("utf-8")

#     if filename == "END": # verifica se os arquivos terminaram
#         print("Todos os arquivos foram recebidos")
#         break

#     new_filename = f"new-{filename}"

#     bytes_read = b""

#     with open(new_filename, "wb") as f:
#         while True:
#             bytes_read, server_address = udp.recvfrom(BUFFER_SIZE) # recebe os dados do arquivo
#             if bytes_read == b"ENDFILE": # verifica se o arquivo terminou
#                 print(f"recebi o arquivo '{filename}'")
#                 break

#             f.write(bytes_read) # escreve os dados recebidos no arquivo criado

#         f.close()


udp.close() # fechar o socket