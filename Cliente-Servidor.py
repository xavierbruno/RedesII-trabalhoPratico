import socket
import threading
import os

# Configuração do nó
SERVER_IP = "192.168.15.106"
SERVER_PORT = 5000
PEER_PORT = 5001  # Porta local para conexões P2P
FILES = ["song1.mp3", "song3.mp3"]  # Arquivos compartilhados pelo nó

# Função para registrar o nó no servidor central
def register_with_server():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((SERVER_IP, SERVER_PORT))
    register_message = f"REGISTER 192.168.15.106:{PEER_PORT} {','.join(FILES)}"
    client.send(register_message.encode())
    response = client.recv(1024).decode()
    print(f"Resposta do servidor: {response}")
    client.close()

# Função para consultar arquivos no servidor central
def list_files_on_server():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((SERVER_IP, SERVER_PORT))
    client.send("LIST".encode())
    response = client.recv(1024).decode()
    print(f"Lista de nós e arquivos:\n{response}")
    client.close()

# Função para requisitar um arquivo de outro nó (P2P)
def request_file_from_peer(peer_ip, peer_port, filename):
    peer_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peer_client.connect((peer_ip, int(peer_port)))
    peer_client.send(f"REQUEST {filename}".encode())
    with open(f"downloads/{filename}", "wb") as f:
        while True:
            data = peer_client.recv(1024)
            if not data:
                break
            f.write(data)
    print(f"Arquivo {filename} baixado com sucesso!")
    peer_client.close()

# Função para lidar com conexões P2P (atuando como servidor P2P)
def handle_peer_connection(conn, addr):
    request = conn.recv(1024).decode()
    command, filename = request.split(" ", 1)
    if command == "REQUEST" and filename in FILES:
        print(f"Enviando arquivo {filename} para {addr}")
        with open(filename, "rb") as f:
            data = f.read(1024)
            while data:
                conn.send(data)
                data = f.read(1024)
        print(f"Arquivo {filename} enviado com sucesso.")
    conn.close()

# Função principal para inicializar o nó
def main():
    # Registrar no servidor central
    register_with_server()

    # Criar um servidor para conexões P2P
    peer_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peer_server.bind(("0.0.0.0", PEER_PORT))
    peer_server.listen(5)
    print(f"Servidor P2P rodando na porta {PEER_PORT}")

    # Interface para o usuário
    threading.Thread(target=lambda: peer_server_loop(peer_server)).start()
    while True:
        print("\nEscolha uma opção:")
        print("1 - Consultar lista de nós e arquivos")
        print("2 - Requisitar arquivo de outro nó")
        print("3 - Sair")
        option = input("Opção: ")
        
        if option == "1":
            list_files_on_server()
        elif option == "2":
            peer_ip = input("IP do nó: ")
            peer_port = input("Porta do nó: ")
            filename = input("Nome do arquivo: ")
            request_file_from_peer(peer_ip, peer_port, filename)
        elif option == "3":
            print("Encerrando...")
            break
        else:
            print("Opção inválida.")

# Loop do servidor P2P para aceitar conexões
def peer_server_loop(peer_server):
    while True:
        conn, addr = peer_server.accept()
        threading.Thread(target=handle_peer_connection, args=(conn, addr)).start()

if __name__ == "__main__":
    if not os.path.exists("downloads"):
        os.mkdir("downloads")
    main()
