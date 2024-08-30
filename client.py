import socket
import time
import serial
import re
import threading


def read_serial(ser, rssi_pattern, data):
    try:
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').rstrip()
                print(f"Received: {line}")

                rssi_match = rssi_pattern.search(line)

                if rssi_match:
                    data['rssi'] = int(rssi_match.group(1))
            
    except KeyboardInterrupt:
        print("Stopping the data extraction.")
    finally:
        ser.close()


def send_rssi_to_server(c, data):
    try:
        while True:
            if data['rssi'] is not None:
                rssi_message = f'RSSI Value: {data["rssi"]}\n'
                
                c.sendall(rssi_message.encode('utf-8'))
                print(f"Sent to server: {rssi_message.strip()}")
                
                response = c.recv(1024).decode('utf-8')
                print(f"Server response: {response}")
            
            time.sleep(5)  # Adjust the time interval as needed

    except KeyboardInterrupt:
        print("Client interrupted.")

    finally:
        c.close()


def main():
    c = socket.socket()
    
    try:
        c.connect(('localhost', 9999))
        print("Connected to server")
    except Exception as e:
        print(f"Failed to connect to server: {e}")
        return
    
    ser = serial.Serial('COM5', 115200, timeout=1)
    time.sleep(2)

    rssi_pattern = re.compile(r"Parsed RSSI value: (-?\d+)")
    data = {'rssi': None}

    # Start a thread for reading serial data
    serial_thread = threading.Thread(target=read_serial, args=(ser, rssi_pattern, data))
    serial_thread.start()

    # Send RSSI data to the server in the main thread
    send_rssi_to_server(c, data)


if __name__ == "__main__":
    main()
