import socket
import time


def main():
    c = socket.socket()
    
    try:
        c.connect(('localhost', 9999))
        print("Connected to server")
    except Exception as e:
        print(f"Failed to connect to server: {e}")
        return

    try:
        while True:
            from terminal_scraper import get_rssi_data, get_distance_data
            rssi_value = get_rssi_data()
            distance_value = get_distance_data()

            if rssi_value is not None and distance_value is not None:

                rssi_message = f'RSSI Value : {rssi_value}'
                distance_message = f'Distance Value : {distance_value}'
                
                c.sendall(rssi_message.encode('utf-8'))
                c.sendall(distance_message.encode('utf-8'))
                
                response = c.recv(1024).decode('utf-8')
                print(f"Server response: {response}")
            
            time.sleep(5)

    except KeyboardInterrupt:
        print("Client interrupted.")

    finally:
        c.close()

if __name__ == "__main__":
    main()
