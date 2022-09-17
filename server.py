import os
from pydoc import cli
import socket

BUFFER_SIZE = 1024

SERVER_IP = '' # '' = significa que ouvira em todas as interfaces

SERVER_PORT = 5002 # Porta que o servidor vai ouvir

SERVER = (SERVER_IP, SERVER_PORT)

expected_num_seq = b'1'

def send_ACK(num_seq, client_address):
    global expected_num_seq

    udp.sendto(expected_num_seq, client_address)
    
    if num_seq == expected_num_seq:
        expected_num_seq =  b'0' if (expected_num_seq == b'1') else b'1'
        print("estou esperando agora", expected_num_seq)

def receive_files(output_directory):
    udp.bind(SERVER) # faz o bind do ip da porta para comecar a ouvir

    try:
        os.mkdir(output_directory) # cria o diretório e entra nele
    except: 
        pass

    os.chdir(output_directory)

    # Recebendo arquivos
    while True:
        filename, client_address = udp.recvfrom(BUFFER_SIZE) # recebe o nome do arquivo

        filename = filename.decode("utf-8")

        num_seq = bytes(filename[0], "utf-8")
        print(f"recebi numero {num_seq}")
        print(f"tava esperando {expected_num_seq}")
        filename = filename[1:]
        
        send_ACK(num_seq, client_address)

        if filename == "END": # verifica se os arquivos terminaram
            print("Todos os arquivos foram recebidos")
            break

        new_filename = f"new-{filename}"

        bytes_read = b""

        with open(new_filename, "wb") as f:
            while True:
                bytes_read, client_address = udp.recvfrom(BUFFER_SIZE) # recebe os dados do arquivo

                bytes_read = bytes_read.decode("utf-8")
                
                num_seq = bytes_read[0]
                num_seq = bytes(num_seq, "utf-8")

                bytes_read = bytes_read.encode("utf-8")

                print("num_seq:", num_seq)
                print("expected:", expected_num_seq)

                bytes_read = bytes_read[1:]

                send_ACK(num_seq, client_address)

                if bytes_read == b"ENDFILE": # verifica se o arquivo terminou
                    print(f"recebi o arquivo '{filename}'")
                    break

                f.write(bytes_read) # escreve os dados recebidos no arquivo criado

            f.close()
    
    # retorna para o root
    os.chdir("../")
    
    return client_address

def send_files(read_dir, client_address):
    # Enviando arquivos

    files = []

    # Leitura de todos os arquivos da pasta
    for i, filename in enumerate(os.listdir(read_dir)): 
        f = os.path.join(read_dir, filename) 

        if os.path.isfile(f): 
            print(filename)
            files.append(filename)

    os.chdir(read_dir) 

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



udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # criando o socket UDP

rcv_directory = "server" # diretório para guardar os arquivos
client_address = receive_files(rcv_directory)

#read_directory = "server" 
#send_files(read_directory, client_address)

udp.close() # fecha o socket