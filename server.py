import os
import socket

BUFFER_SIZE = 1024

SERVER_IP = '' # '' = significa que ouvira em todas as interfaces

SERVER_PORT = 5001 # Porta que o servidor vai ouvir

udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # criando o socket UDP

SERVER = (SERVER_IP, SERVER_PORT)

msg_decoded = ""

directory = "new_files" # diretório para guardar os arquivos

udp.bind(SERVER) # faz o bind do ip da porta para comecar a ouvir

try:
    os.mkdir(directory) # cria o diretório e entra nele
except: 
    pass

os.chdir(directory)

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

udp.close() # fecha o socket