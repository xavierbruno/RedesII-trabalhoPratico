import socket
import threading

# Tabela dinâmica de clientes
clients = {}

def handle_client(conn, addr):
    global clients
    print(f"Nova conexão: {addr}")
    
    while True:
        try:
            data = conn.recv(1024).decode()
            if not data:
                break
            
            print(f"Mensagem recebida de {addr}: {data}")
            command = data.split(" ", 1)[0].upper()
            
            if command == "REGISTER":
                _, client_data = data.split(" ", 1)
                ip_port, files = client_data.split(" ", 1)
                if ip_port in clients:
                    conn.send("Cliente já registrado.\n".encode())
                else:
                    clients[ip_port] = files.split(",")
                    conn.send("Registro realizado com sucesso.\n".encode())
                    print(f"Cliente registrado: {ip_port} com arquivos {clients[ip_port]}")

            elif command == "LIST":
                client_list = "\n".join(
                    [f"{ip}: {', '.join(files)}" for ip, files in clients.items()]
                )
                conn.send(f"Nós conectados:\n{client_list}\n".encode())
            
            elif command == "UNREGISTER":
                ip_port = data.split(" ", 1)[1]
                if ip_port in clients:
                    del clients[ip_port]
                    conn.send("Registro removido com sucesso.\n".encode())
                    print(f"Cliente removido: {ip_port}")
                else:
                    conn.send("Cliente não encontrado.\n".encode())
            
            elif command == "QUIT":
                conn.send("Conexão encerrada.\n".encode())
                break

            else:
                conn.send("Comando inválido.\n".encode())

        except Exception as e:
            print(f"Erro no cliente {addr}: {e}")
            break

    conn.close()
    print(f"Conexão encerrada com {addr}")

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 5000))
    server.listen(5)
    print("Servidor iniciado na porta 5000.")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == "__main__":
    main()
