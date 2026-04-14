import socket
import threading
import sys

class Servidor:
    def __init__(self, host='', port=8000):
        self.clients = {} # {socket: nombre}
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_sock.bind((host, port))
        self.server_sock.listen(5)
        
        print(f"--- Servidor de Chat Activo ---")
        print("ADMIN: /usuarios, /msg [texto], /privado [nombre] [texto], /salir")
        print("INFO: Los usuarios pueden usar @nombre para mensajes privados.")

        threading.Thread(target=self.acept_client, daemon=True).start()
        self.admin_console()

    def admin_console(self):
        while True:
            cmd = input('')
            if cmd == '/usuarios':
                print(f"Conectados ({len(self.clients)}): " + ", ".join(self.clients.values()))
            elif cmd.startswith('/msg '):
                self.broadcast(f"[SERVIDOR]: {cmd[5:]}", None)
            elif cmd.startswith('/privado '):
                try:
                    _, destino, contenido = cmd.split(' ', 2)
                    self.send_direct(f"[ADMN -> Tú]: {contenido}", destino)
                except: print("Error. Uso: /privado [nombre] [texto]")
            elif cmd == '/salir':
                self.broadcast("### SERVIDOR CERRADO POR EL ADMIN ###", None)
                for s in list(self.clients.keys()): s.close()
                self.server_sock.close()
                sys.exit()

    def acept_client(self):
        while True:
            try:
                client_sock, addr = self.server_sock.accept()
                username = client_sock.recv(1024).decode('utf-8')
                
                # Evitar nombres duplicados
                if username in self.clients.values():
                    username = f"{username}_{addr[1]}" 

                self.clients[client_sock] = username
                self.broadcast(f"*** {username} se ha unido ***", client_sock)
                print(f"LOG: {username} conectado.")
                
                threading.Thread(target=self.handle_client, args=(client_sock,), daemon=True).start()
            except: break

    def handle_client(self, client_sock):
        while True:
            try:
                msg = client_sock.recv(1024).decode('utf-8')
                if not msg or msg == "exit": raise Exception()
                
                nombre_origen = self.clients[client_sock]

                #mensaje privado entre usuarios
                if msg.startswith('@'):
                    try:
                        nombre_destino, contenido = msg[1:].split(' ', 1)
                        exito = self.send_direct(f"[Privado de {nombre_origen}]: {contenido}", nombre_destino)
                        if not exito:
                            client_sock.send(f"Error: El usuario {nombre_destino} no existe.".encode('utf-8'))
                    except ValueError:
                        client_sock.send("Formato privado incorrecto. Usa: @nombre mensaje".encode('utf-8'))
                
                # Mensaje público
                else:
                    print(f"{nombre_origen}: {msg}")
                    self.broadcast(f"{nombre_origen}: {msg}", client_sock)
            except:
                if client_sock in self.clients:
                    n = self.clients[client_sock]
                    del self.clients[client_sock]
                    client_sock.close()
                    self.broadcast(f"*** {n} ha salido ***", None)
                    print(f"LOG: {n} desconectado.")
                break

    def broadcast(self, msg, sender_sock):
        for client in list(self.clients.keys()):
            if client != sender_sock:
                try: client.send(msg.encode('utf-8'))
                except: pass

    def send_direct(self, msg, nombre_destino):
        """Busca a un usuario por nombre y le envía un mensaje"""
        for sock, nombre in self.clients.items():
            if nombre == nombre_destino:
                try:
                    sock.send(msg.encode('utf-8'))
                    return True
                except: return False
        return False

if __name__ == "__main__":
    Servidor()
