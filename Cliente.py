import socket

def main():
    server_ip = "192.168.15.106"
    server_port = 5000

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((server_ip, server_port))
    print("Conectado ao servidor.")

    while True:
        print("\nEscolha uma opção:")
        print("1 - Registrar cliente")
        print("2 - Consultar lista de nós")
        print("3 - Encerrar registro")
        print("4 - Sair")

        option = input("Opção: ")
        
        if option == "1":
            ip_port = input("Informe seu IP:Porta : ")
            files = input("Informe a lista de arquivos separados por vírgula: ")
            message = f"REGISTER {ip_port} {files}"
            client.send(message.encode())
        
        elif option == "2":
            client.send("LIST".encode())
        
        elif option == "3":
            ip_port = input("Informe seu IP:Porta para remoção : ")
            message = f"UNREGISTER {ip_port}"
            client.send(message.encode())
        
        elif option == "4":
            client.send("QUIT".encode())
            break
        
        else:
            print("Opção inválida.")
            continue
        
        # Receber resposta do servidor
        response = client.recv(1024).decode()
        print(f"Resposta do servidor: {response}")
    
    client.close()
    print("Conexão encerrada.")

if __name__ == "__main__":
    main()
