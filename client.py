import os
import socket

BUFFER_SIZE = 1024 # tamanho do buffer

SERVER_IP = "localhost" # endereco IP do servidor

SERVER_PORT = 5002 # porta que o servidor esta esperando a msg

SERVER_DEST = (SERVER_IP, SERVER_PORT)

num_seq = b'0' # número de sequencia inicial

expected_num_seq = b'1' # primeiro número de sequencia esperado

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

def send_pkt(msg):
    global num_seq

    num_seq = b'0' if (num_seq == b'1') else b'1'

    while True:
        pkt = num_seq + msg
        udp.sendto(pkt, SERVER_DEST) # enviar o pacote em bytes enquanto tiver
        try:
            if correct_ACK():
                break
        except socket.timeout:
            continue

# Enviando arquivos

def send_files(read_dir):
    # Leitura de todos os arquivos da pasta
    
    for i, filename in enumerate(os.listdir(read_dir)): 
        f = os.path.join(read_dir, filename) 
        
        if os.path.isfile(f): 
            print(filename)
            files.append(filename)

    os.chdir(read_dir) 

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

    os.chdir("../")
    print("Todos os arquivos foram enviados")

    send_pkt(b"END")

def rcv_files(output_directory):
    try:
        os.mkdir(output_directory) # cria o diretório e entra nele
    except: 
        pass

    os.chdir(output_directory)

    # Recebendo arquivos
    while True:
        try:
            filename, server_address = udp.recvfrom(BUFFER_SIZE) # recebe o nome do arquivo

        except socket.timeout:
            if server_address is not None:
                udp.sendto(num_seq, server_address)
            continue

        filename = filename.decode("utf-8")

        num_seq = bytes(filename[0], "utf-8") # número de sequencia no primeiro byte recebido
        filename = filename[1:] # todo o resto são dados

        send_ACK(num_seq, server_address)

        if filename == "END": # verifica se os arquivos terminaram
            print("Todos os arquivos foram recebidos")
            break

        new_filename = f"new-{filename}"

        bytes_read = b""

        with open(new_filename, "wb") as f:
            while True:
                bytes_read, server_address = udp.recvfrom(BUFFER_SIZE) # recebe os dados do arquivo
                
                num_seq = bytes_read[0]
                
                # converte o número de sequencia para bytes
                if num_seq == 48:
                    num_seq = b'0'
                if num_seq == 49:
                    num_seq = b'1'

                bytes_read = bytes_read[1:]

                send_ACK(num_seq, server_address)

                if bytes_read == b"ENDFILE": # verifica se o arquivo terminou
                    print(f"recebi o arquivo '{filename}'")
                    break

                f.write(bytes_read) # escreve os dados recebidos no arquivo criado

            f.close()

    os.chdir("../")

udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # criando o socket udp
udp.settimeout(0.3)

files = []

read_dir = 'origin'
send_files(read_dir)

rcv_dir = "destiny"

rcv_files(rcv_dir)

udp.close() # fechar o socket