import os
import socket

BUFFER_SIZE = 1024

SERVER_IP = '' # '' = significa que ouvira em todas as interfaces

SERVER_PORT = 5001 # Porta que o servidor vai ouvir

udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # criando o socket UDP

SERVER = (SERVER_IP, SERVER_PORT)

directory = "server" # diretório para guardar os arquivos

udp.bind(SERVER) # faz o bind do ip da porta para comecar a ouvir

try:
    os.mkdir(directory) # cria o diretório e entra nele
except: 
    pass

os.chdir(directory)

# Recebendo arquivos
while True:
    filename, client_address = udp.recvfrom(BUFFER_SIZE) # recebe o nome do arquivo
    filename = filename.decode("utf-8")

    if filename == "END": # verifica se os arquivos terminaram
        print("Todos os arquivos foram recebidos")
        break

    new_filename = f"new-{filename}"

    bytes_read = b""

    with open(new_filename, "wb") as f:
        while True:
            bytes_read, client_address = udp.recvfrom(BUFFER_SIZE) # recebe os dados do arquivo
            if bytes_read == b"ENDFILE": # verifica se o arquivo terminou
                print(f"recebi o arquivo '{filename}'")
                break

            f.write(bytes_read) # escreve os dados recebidos no arquivo criado

        f.close()

# Enviando arquivos

os.chdir("../")

files = []

# Leitura de todos os arquivos da pasta
directory = 'server'
for i, filename in enumerate(os.listdir(directory)): 
    f = os.path.join(directory, filename) 

    if os.path.isfile(f): 
        print(filename)
        files.append(filename)

os.chdir(directory) 

for file in files:
    filename_encoded = bytes(file, "utf-8") # codificar o nome do arquivo
    udp.sendto(filename_encoded, client_address) # enviar o nome do arquivo para o cliente
    
    with open(file, "rb") as f:
        while True:
            bytes_read = f.read(BUFFER_SIZE) # ler o arquivo
            if not bytes_read:
                print(f"arquivo '{file}' enviado") 
                udp.sendto(b"ENDFILE", client_address) # flag de fim do arquivo 
                break
            else:
                udp.sendto(bytes_read, client_address) # enviar o arquivo em bytes enquanto tiver

        f.close()

print("Todos os arquivos foram enviados")
udp.sendto (b"END", client_address) # flag de fim de todos os arquivos da pasta

udp.close() # fecha o socket