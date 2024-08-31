import numpy as np
from scipy.optimize import least_squares
import socket
import threading

# Define the known positions of the ESP32 devices
positions = np.array([
    [0, 0, 0],   # Position of the first ESP32
    [2, 0, 0],   # Position of the second ESP32
    [0, 2, 0]    # Position of the third ESP32
])

def calculate_distance(rssi):
    A = -69  # RSSI at 1 meter
    n = 2.0  # Path loss exponent
    return pow(10, (A - rssi) / (10 * n))

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
            # Receive all data from the client
            data = c.recv(1024).decode('utf-8').strip()
            if not data:
                break

            # Split the received data by newlines and process each line
            rssi_values = data.split('\n')
            if len(rssi_values) < 3:
                print("Received insufficient data.")
                continue

            # Convert RSSI values to distances
            distances = []
            for rssi_value in rssi_values:
                try:
                    rssi = float(rssi_value)
                    distance = calculate_distance(rssi)
                    distances.append(distance)
                except ValueError:
                    print(f"Invalid RSSI value received: {rssi_value}")
                    continue

            # Check if we have received exactly 3 distances
            if len(distances) == 3:
                # Perform trilateration
                estimated_position = trilateration(positions, distances)
                print("Estimated Position:", estimated_position)

                # Send back the estimated position to the client
                response = f"Estimated Position: {estimated_position.tolist()}\n"
                c.sendall(response.encode('utf-8'))

                # Optionally plot the spheres
                import matplotlib.pyplot as plt
                from mpl_toolkits.mplot3d import Axes3D

                def plot_spheres(positions, distances):
                    fig = plt.figure()
                    ax = fig.add_subplot(111, projection='3d')

                    # Plot spheres
                    u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
                    x = np.cos(u) * np.sin(v)
                    y = np.sin(u) * np.sin(v)
                    z = np.cos(v)

                    for (pos, dist) in zip(positions, distances):
                        ax.plot_surface(pos[0] + dist * x, pos[1] + dist * y, pos[2] + dist * z, color='b', alpha=0.1)

                    # Plot the estimated position
                    ax.scatter(*estimated_position, color='r', s=100, label='Estimated Position')

                    ax.set_xlabel('X')
                    ax.set_ylabel('Y')
                    ax.set_zlabel('Z')
                    plt.legend()
                    plt.show()

                plot_spheres(positions, distances)
            else:
                print("Received incorrect number of distances.")

    except Exception as e:
        print(f"Error in handling client: {e}")
    finally:
        c.close()

def start_server():
    s = socket.socket()
    s.bind(('0.0.0.0', 8080))
    s.listen(5)
    print('Server listening on port 8080...')

    while True:
        c, addr = s.accept()
        print(f"Connected with {addr}")
        client_thread = threading.Thread(target=handle_client_connection, args=(c,))
        client_thread.start()

if __name__ == "__main__":
    start_server()
