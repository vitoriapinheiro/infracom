import os
import socket

BUFFER_SIZE = 1024 # tamanho do buffer

SERVER_IP = "localhost" # endereco IP do servidor

SERVER_PORT = 5001 # porta que o servidor esta esperando a msg

SERVER_DEST = (SERVER_IP, SERVER_PORT)

udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # criando o socket udp

msg  = ""

files = []

# Leitura de todos os arquivos da pasta
directory = 'files'
for i, filename in enumerate(os.listdir(directory)): 
    f = os.path.join(directory, filename) 
    
    if os.path.isfile(f): 
        print(filename)
        files.append(filename)

os.chdir(directory) 

for file in files:
    filename_encoded = bytes(file, "utf-8") # codificar o nome do arquivo
    udp.sendto(filename_encoded, SERVER_DEST) # enviar o nome do arquivo para o servidor
    
    with open(file, "rb") as f:
        while True:
            bytes_read = f.read(BUFFER_SIZE) # ler o arquivo
            if not bytes_read:
                print(f"arquivo '{file}' enviado") 
                udp.sendto(b"ENDFILE", SERVER_DEST) # flag de fim do arquivo 
                break
            else:
                udp.sendto(bytes_read, SERVER_DEST) # enviar o arquivo em bytes enquanto tiver

        f.close()

print("Todos os arquivos foram enviados")
udp.sendto (b"END", SERVER_DEST) # flag de fim de todos os arquivos da pasta

udp.close() # fechar o socket