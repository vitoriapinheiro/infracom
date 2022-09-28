import os
import socket

BUFFER_SIZE = 1024

SERVER_IP = '' # '' = significa que ouvira em todas as interfaces

SERVER_PORT = 5002 # Porta que o servidor vai ouvir

SERVER = (SERVER_IP, SERVER_PORT)

num_seq = b'0' # número de sequencia inicial

packet_counter = 0

expected_num_seq = b'1' # primeiro número de sequencia esperado

client_address = None

def send_ACK(num_seq, client_address):
    global expected_num_seq

    udp.sendto(expected_num_seq, client_address) # envia o ACK com o número de sequencia esperado
    
    if num_seq == expected_num_seq: # se o que foi recebido era o esperado, muda o número esperado
        expected_num_seq =  b'0' if (expected_num_seq == b'1') else b'1'

def correct_ACK():
    global num_seq


    ACK_msg, _ = udp.recvfrom(1) # espera receber o ACK


    if (ACK_msg == num_seq):
        return True
    else:
        return False

def send_pkt(msg, address):
    global num_seq

    num_seq = b'0' if (num_seq == b'1') else b'1'

    while True:
        pkt = num_seq + msg
        udp.sendto(pkt, address) # enviar o pacote em bytes enquanto tiver
        try:
            if correct_ACK():
                break
        except socket.timeout:
            continue


def receive_files(output_directory):
    global packet_counter, client_address
    udp.bind(SERVER) # faz o bind do ip da porta para comecar a ouvir
    try:
        os.mkdir(output_directory) # cria o diretório e entra nele
    except: 
        pass

    os.chdir(output_directory)

    # Recebendo arquivos
    while True:
        try:
            filename, client_address = udp.recvfrom(BUFFER_SIZE) # recebe o nome do arquivo

        except socket.timeout:
            if client_address is not None:
                udp.sendto(num_seq, client_address)
            continue

        filename = filename.decode("utf-8")

        num_seq = bytes(filename[0], "utf-8") # número de sequencia no primeiro byte recebido
        filename = filename[1:] # todo o resto são dados    
        
        send_ACK(num_seq, client_address)

        if filename == "END": # verifica se os arquivos terminaram
            print("Todos os arquivos foram recebidos")
            break

        new_filename = f"new-{filename}"

        bytes_read = b""

        with open(new_filename, "wb") as f:
            while True:
                bytes_read, client_address = udp.recvfrom(BUFFER_SIZE) # recebe os dados do arquivo
                
                num_seq = bytes_read[0]
                
                # converte o número de sequencia para bytes
                if num_seq == 48:
                    num_seq = b'0'
                if num_seq == 49:
                    num_seq = b'1'

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
        
        send_pkt(filename_encoded, client_address)


        with open(file, "rb") as f:
            while True:
                bytes_read = f.read(BUFFER_SIZE-1) # ler o arquivo
                if not bytes_read:
                    print(f"arquivo '{file}' enviado") 
                    send_pkt(b"ENDFILE", client_address) # flag de fim do arquivo 
                    break
                else:
                    send_pkt(bytes_read, client_address)

            f.close()

    os.chdir("../")

    print("Todos os arquivos foram enviados")
    send_pkt(b"END",client_address)  # flag de fim de todos os arquivos da pasta


udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # criando o socket UDP
udp.settimeout(0.3) # timer 0.3 segundos

rcv_directory = "server" # diretório para guardar os arquivos
client_address = receive_files(rcv_directory)

read_directory = "server" 
send_files(read_directory, client_address)

udp.close() # fecha o socket