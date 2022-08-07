import os
import socket
import threading

BUFFER_SIZE = 1024

SERVER_IP = "localhost" # endereco IP do servidor

SERVER_PORT = 5000 # porta que o servidor esta esperando a msg

SERVER_DEST = (SERVER_IP, SERVER_PORT)

udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# criando o socket udp

msg  = ""

files = []

# Leitura de todos os jogos da pasta
directory = 'files'
for i, filename in enumerate(os.listdir(directory)): 
    f = os.path.join(directory, filename) 
    
    if os.path.isfile(f): 
        print(filename)
        files.append(filename)

os.chdir(directory)

for file in files:
    filename_encoded = bytes(file, "utf-8")
    udp.sendto (filename_encoded, SERVER_DEST)
    
    with open(file, "rb") as f:
        while True:
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                print("mandou um arquivo todo - cliente") 
                udp.sendto (b"ENDFILE", SERVER_DEST)               
                # file transmitting is done
                break

            udp.sendto (bytes_read, SERVER_DEST)

        f.close()

udp.sendto (b"END", SERVER_DEST)

udp.close()

# """
# while(msg != "END"):

#     SERVER_DEST = (SERVER_IP, SERVER_PORT)

#     msg = input("Digite uma mensagem: ")

#     udp.sendto (bytes(msg, "utf8"), SERVER_DEST)
#     # enviar mensagem para o destino desejado
#     # deve-se converter para bytes
# """

#udp.close()