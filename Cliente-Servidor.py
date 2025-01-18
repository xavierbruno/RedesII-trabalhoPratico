import socket
import threading
import os

class NoP2P:
    def __init__(self, host='127.0.0.1', porta_tcp=5001, porta_udp=6001):
        self.host = host
        self.porta_tcp = porta_tcp
        self.porta_udp = porta_udp
        self.arquivos = ["song1.mp3", "song3.mp3"]
        self.servidor_central = ('127.0.0.1', 5000)

    def iniciar(self):
        threading.Thread(target=self.iniciar_servidor).start()
        self.menu_cliente()

    def iniciar_servidor(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
            udp_socket.bind((self.host, self.porta_udp))
            print(f"Servidor P2P iniciado em {self.host}:{self.porta_udp} para streaming UDP")

            while True:
                dados, addr = udp_socket.recvfrom(1024)
                requisicao = dados.decode().split('|')
                if requisicao[0] == 'REQUISITAR':
                    arquivo = requisicao[1]
                    self.enviar_arquivo_udp(udp_socket, addr, arquivo)

    def enviar_arquivo_udp(self, endereco_cliente, arquivo):
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            if not os.path.exists(arquivo):
                # Enviar mensagem de erro se o arquivo não existir
                mensagem = "ERRO: Arquivo não encontrado."
                udp_socket.sendto(mensagem.encode(), endereco_cliente)
                print(f"Arquivo {arquivo} não encontrado. Notificando cliente.")
                return

            print(f"Iniciando envio do arquivo {arquivo} para {endereco_cliente}")
            with open(arquivo, "rb") as f:
                while True:
                    dados = f.read(1024)
                    if not dados:
                        udp_socket.sendto(b'END', endereco_cliente)  # Fim da transferência
                        print("Envio concluído!")
                        break
                    udp_socket.sendto(dados, endereco_cliente)
        except Exception as e:
            print(f"[Erro] Falha ao enviar arquivo: {e}")
        finally:
            udp_socket.close()

    def menu_cliente(self):
        while True:
            print("\n1 - Registrar Cliente")
            print("2 - Consultar Lista de Nós e Arquivos")
            print("3 - Requisitar Arquivo")
            print("4 - Encerrar Conexão")
            opcao = input("Escolha uma opção: ")

            if opcao == '1':
                self.registrar_cliente()
            elif opcao == '2':
                self.consultar_lista_nos()
            elif opcao == '3':
                self.requisitar_arquivo()
            elif opcao == '4':
                self.encerrar_conexao()
                break

    def registrar_cliente(self):
        self.arquivos = input("Digite os arquivos disponíveis separados por vírgula: ").split(',')
        endereco = f"{self.host}:{self.porta_tcp}"
        mensagem = f"REGISTRAR|{endereco}|{','.join(self.arquivos)}"
        self.enviar_para_servidor(mensagem)

    def consultar_lista_nos(self):
        mensagem = "CONSULTAR"
        resposta = self.enviar_para_servidor(mensagem)
        print("\nNós e arquivos disponíveis:")
        print(resposta)

    def requisitar_arquivo(self):
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Indentado corretamente
        udp_socket.settimeout(5)  # Timeout para evitar travamento

        ip = input("Digite o IP do nó: ")
        porta = int(input("Digite a porta UDP do nó: "))
        arquivo = input("Digite o nome do arquivo: ")

        try:
            # Enviar solicitação ao servidor
            mensagem = f"GET {arquivo}"
            udp_socket.sendto(mensagem.encode(), (ip, porta))
            print(f"Solicitação enviada para {ip}:{porta}")

            # Receber os dados do arquivo
            with open(f"recebido_{arquivo}", "wb") as f:
                while True:
                    try:
                        dados, _ = udp_socket.recvfrom(1024)
                        if dados == b'END':  # Indicação de fim da transferência
                            print("Transferência concluída!")
                            break
                        f.write(dados)
                    except socket.timeout:
                        print("Tempo limite atingido para receber dados.")
                        break
        except ConnectionResetError:
            print(f"[Erro] Conexão com {ip}:{porta} foi encerrada.")
        except Exception as e:
            print(f"[Erro] Falha ao requisitar arqu ivo: {e}")
        finally:
            udp_socket.close()


    def encerrar_conexao(self):
        endereco = f"{self.host}:{self.porta_tcp}"
        mensagem = f"ENCERRAR|{endereco}"
        self.enviar_para_servidor(mensagem)

    def enviar_para_servidor(self, mensagem):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
            tcp_socket.connect(self.servidor_central)
            tcp_socket.sendall(mensagem.encode())
            resposta = tcp_socket.recv(1024).decode()
            return resposta

if __name__ == '__main__':
    no = NoP2P()
    no.iniciar()
