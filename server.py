import os
import socket

BUFFER_SIZE = 1024

SERVER_IP = '' # '' = significa que ouvira em todas as interfaces

SERVER_PORT = 5000 # Porta que o servidor vai ouvir

udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # criando o socket UDP

SERVER = (SERVER_IP, SERVER_PORT)

msg_decoded = ""

directory = "new_files"

udp.bind(SERVER)
# faz o bind do ip da porta para comecar a ouvir

os.mkdir(directory)
os.chdir(directory)

while True:
    filename_msg, client_address = udp.recvfrom(BUFFER_SIZE)

    if filename_msg == b"END":
        print("acabei tudo - server")
        break

    filename = f"new-{filename_msg.decode('utf-8')}"

    bytes_read = b""

    with open(filename, "wb") as f:
        while True:
            bytes_read, _ = udp.recvfrom(BUFFER_SIZE)
            print("------------file arrived-------------")
            if bytes_read == b"ENDFILE":
                print("recebi arquivo - server")
                break # acabou o arquivo

            f.write(bytes_read)

        f.close()

udp.close()

# while(msg_decoded != "\END"):

#     msg_bytes, end_cliente = udp.recvfrom(1024)
#     # o parametro indica o tamanho do buffer de recebimento (deve ser potencia de 2)
#     # retorna uma string de dados e o endereco de de quem enviou

#     msg_decoded = msg_bytes.decode("utf-8")


#     print(f"Recebi {msg_decoded} do cliente {end_cliente}")

# udp.close() # fim do socket