import socket
import threading
import sys

class Cliente:
    def __init__(self, host='10.3.66.22', port=8000):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            self.sock.connect((host, port))
        except Exception as e:
            print(f"Error de conexión: {e}")
            return

        self.username = input("Ingresa tu nombre de usuario: ")
        self.sock.send(self.username.encode('utf-8'))

        # Hilo para recibir mensajes del servidor
        threading.Thread(target=self.recv_msg, daemon=True).start()

        print("--- Conectado. Escribe 'exit' para salir ---")
        self.send_msg()

    def send_msg(self):
        while True:
            msg = input()
            try:
                self.sock.send(msg.encode('utf-8'))
                if msg == "exit":
                    self.sock.close()
                    sys.exit()
            except:
                break

    def recv_msg(self):
        while True:
            try:
                data = self.sock.recv(1024).decode('utf-8')
                if not data:
                    break
                print(f"\r{data}\n> ", end="")
            except:
                print("\nConexión perdida con el servidor.")
                break

if __name__ == "__main__":
    Cliente()