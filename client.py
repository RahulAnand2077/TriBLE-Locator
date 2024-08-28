import socket

# Define server address and port
SERVER_HOST = 'your_server_ip'  # Replace with your server's IP address
SERVER_PORT = 5000

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((SERVER_HOST, SERVER_PORT))
    print(f"Connected to server at {SERVER_HOST}:{SERVER_PORT}")

    try:
        while True:
            data = input("Enter data to send: ")
            if data.lower() == 'exit':
                break
            client.send(data.encode('utf-8'))
            response = client.recv(1024).decode('utf-8')
            print(f"Received from server: {response}")
    except KeyboardInterrupt:
        pass
    finally:
        client.close()
        print("Connection closed.")

if __name__ == "__main__":
    main()
