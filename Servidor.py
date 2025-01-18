import socket
import threading

class ServidorCentral:
    def __init__(self, host='127.0.0.1', port=5000):
        self.host = host
        self.port = port
        self.nos_registrados = {}
        self.lock = threading.Lock()

    def iniciar(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((self.host, self.port))
            server_socket.listen()
            print(f"Servidor central iniciado em {self.host}:{self.port}")

            while True:
                conn, addr = server_socket.accept()
                threading.Thread(target=self.tratar_cliente, args=(conn, addr)).start()

    def tratar_cliente(self, conn, addr):
        with conn:
            while True:
                dados = conn.recv(1024).decode()
                if not dados:
                    break
                comandos = dados.split('|')
                if comandos[0] == 'REGISTRAR':
                    self.registrar_cliente(conn, comandos[1], comandos[2])
                elif comandos[0] == 'CONSULTAR':
                    self.enviar_lista_nos(conn)
                elif comandos[0] == 'ENCERRAR':
                    self.remover_cliente(conn, comandos[1])

    def registrar_cliente(self, conn, endereco, arquivos):
        with self.lock:
            if endereco in self.nos_registrados:
                conn.sendall(b'CLIENTE_JA_REGISTRADO')
            else:
                self.nos_registrados[endereco] = arquivos.split(',')
                conn.sendall(b'REGISTRO_SUCESSO')
                print(f"Cliente registrado: {endereco} com arquivos: {arquivos}")

    def enviar_lista_nos(self, conn):
        with self.lock:
            lista_nos = '|'.join([f"{k}:{','.join(v)}" for k, v in self.nos_registrados.items()])
            conn.sendall(lista_nos.encode())

    def remover_cliente(self, conn, endereco):
        with self.lock:
            if endereco in self.nos_registrados:
                del self.nos_registrados[endereco]
                conn.sendall(b'CLIENTE_REMOVIDO')
                print(f"Cliente removido: {endereco}")

if __name__ == '__main__':
    servidor = ServidorCentral()
    servidor.iniciar()
