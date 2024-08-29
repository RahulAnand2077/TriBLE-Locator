import socket

def start_server():
    s = socket.socket()
    print('Socket Created')

    s.bind(('localhost', 9999))
    s.listen(2)

    print('Waiting for Connections')

    while True:
        try:
            c, addr = s.accept()
            print('Connected with', addr)

            while True:
                data = c.recv(1024).decode()
                if not data:
                    print("No data received. Client may have disconnected.")
                    break 
                
                print('Received from client:', data)

                response = "Data received"
                c.sendall(response.encode('utf-8'))

        except Exception as e:
            print(f"Error: {e}")

        finally:
            c.close()

if __name__ == "__main__":
    start_server()
