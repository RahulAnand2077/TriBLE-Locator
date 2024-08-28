import socket
import threading

# Define host and port
HOST = '0.0.0.0'  # Listen on all available interfaces
PORT = 5000

# Function to handle client connections
def handle_client(client_socket, addr):
    print(f"Connection established with {addr}")
    while True:
        data = client_socket.recv(1024).decode('utf-8')
        if not data:
            print(f"Connection closed by {addr}")
            break
        print(f"Received from {addr}: {data}")
        client_socket.send(f"Data received: {data}".encode('utf-8'))
    client_socket.close()

# Main server function
def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"Server listening on {HOST}:{PORT}")

    while True:
        client_socket, addr = server.accept()
        client_handler = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_handler.start()

if __name__ == "__main__":
    main()
