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
    except Exception as e:
        print(f"Error reading serial data: {e}")
    finally:
        ser.close()

def send_rssi_to_server(c, data):
    try:
        while True:
            if data['rssi'] is not None:
                rssi_message = f'{data["rssi"]}\n'  # Assuming same RSSI for all ESP32s
                print(f"Sending to server (1): {rssi_message.strip()}")

                try:
                    c.sendall(rssi_message.encode('utf-8'))
                    response = c.recv(1024).decode('utf-8')
                    print(f"Server response: {response}")
                except socket.error as e:
                    print(f"Socket error: {e}")
                    break

            time.sleep(5)  # Adjust time interval as needed

    except Exception as e:
        print(f"Error sending data to server: {e}")
    finally:
        c.close()

def main():
    c = socket.socket()
    
    try:
        c.connect(('192.168.1.52', 8080))
        print("Connected to server")
    except socket.error as e:
        print(f"Failed to connect to server: {e}")
        return
    
    try:
        ser = serial.Serial('COM5', 115200, timeout=1)
    except serial.SerialException as e:
        print(f"Failed to open serial port: {e}")
        return

    rssi_pattern = re.compile(r"Parsed RSSI value 1: (-?\d+)")
    data = {'rssi': None}

    serial_thread = threading.Thread(target=read_serial, args=(ser, rssi_pattern, data))
    serial_thread.start()

    try:
        send_rssi_to_server(c, data)
    except KeyboardInterrupt:
        print("Client interrupted.")
    finally:
        serial_thread.join()
        ser.close()
        c.close()

if __name__ == "__main__":
    main()
