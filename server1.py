import numpy as np
from scipy.optimize import least_squares
import socket
import threading

# Define the known positions of the ESP32 devices
positions = np.array([
    [0, 0, 0],   # Position of the first ESP32
    [1, 0, 0],   # Position of the second ESP32
    [0, 1, 0]    # Position of the third ESP32
])

def trilateration(positions, distances):
    def equations(p):
        x, y, z = p
        return [
            np.sqrt((x - positions[0][0])**2 + (y - positions[0][1])**2 + (z - positions[0][2])**2) - distances[0],
            np.sqrt((x - positions[1][0])**2 + (y - positions[1][1])**2 + (z - positions[1][2])**2) - distances[1],
            np.sqrt((x - positions[2][0])**2 + (y - positions[2][1])**2 + (z - positions[2][2])**2) - distances[2]
        ]

    initial_guess = np.mean(positions, axis=0)
    result = least_squares(equations, initial_guess)
    return result.x

def handle_client_connection(c):
    try:
        while True:
            data = c.recv(1024).decode('utf-8')
            if not data:
                break
            print(f"Received data: {data.strip()}")

            rssi_values = [float(x) for x in data.strip().split(',')]
            distances = np.array(rssi_values)  # Convert RSSI to distance here if needed

            # Perform trilateration
            estimated_position = trilateration(positions, distances)
            print("Estimated Position:", estimated_position)

            # Send back the estimated position to the client
            response = f"Estimated Position: {estimated_position.tolist()}\n"
            c.sendall(response.encode('utf-8'))

    except Exception as e:
        print(f"Error in handling client: {e}")
    finally:
        c.close()

def start_server():
    s = socket.socket()
    s.bind(('localhost', 9999))
    s.listen(2)
    print('Server listening on port 9999...')

    while True:
        c, addr = s.accept()
        print(f"Connected with {addr}")
        client_thread = threading.Thread(target=handle_client_connection, args=(c,))
        client_thread.start()

if __name__ == "__main__":
    start_server()
