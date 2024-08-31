import numpy as np
from scipy.optimize import least_squares
import socket
import threading
import queue
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import Tk, Frame

# Define the known positions of the ESP32 devices
positions = np.array([
    [10, 0, 0],   # Position of the first ESP32
    [0, 10, 0],   # Position of the second ESP32
    [0, 0, 10]    # Position of the third ESP32
])

# Dictionary to store RSSI values for each client (indexed by client_id)
rssi_data = {}

# Queue for communicating data between threads
plot_queue = queue.Queue()

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

def handle_client_connection(c, client_id):
    global plot_queue
    try:
        buffer = ""
        while True:
            data = c.recv(1024).decode('utf-8').strip()
            if not data:
                break
            buffer += data
            
            # Check for end of a complete message
            if "\n" in buffer:
                messages = buffer.split("\n")
                for message in messages:
                    if message:
                        print(f"Received data from client {client_id}: {message}")
                        try:
                            rssi = float(message)
                            distance = calculate_distance(rssi)

                            rssi_data[client_id] = distance

                            if len(rssi_data) == 3:
                                distances = np.array([rssi_data[0], rssi_data[1], rssi_data[2]])
                                estimated_position = trilateration(positions, distances)
                                print("Estimated Position:", estimated_position)

                                response = f"Estimated Position: {estimated_position.tolist()}\n"
                                for cid in rssi_data:
                                    c.sendall(response.encode('utf-8'))

                                plot_queue.put((positions, distances, estimated_position))
                                rssi_data.clear()
                        except ValueError:
                            print(f"Invalid data received from client {client_id}: {message}")
                buffer = ""  # Clear buffer after processing all messages
    except Exception as e:
        print(f"Error in handling client {client_id}: {e}")
    finally:
        c.close()

def plot_in_main_thread():
    root = Tk()
    root.title("3D Plot")

    frame = Frame(root)
    frame.pack(side='top', fill='both', expand=1)

    fig = plt.Figure(figsize=(8, 6), dpi=100)
    ax = fig.add_subplot(111, projection='3d')

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.get_tk_widget().pack(side='top', fill='both', expand=1)

    def update_plot():
        if not plot_queue.empty():
            positions, distances, estimated_position = plot_queue.get()
            plot_spheres(ax, positions, distances, estimated_position)
            canvas.draw()
        root.after(100, update_plot)

    root.after(100, update_plot)  # Schedule the plot update
    root.mainloop()

def plot_spheres(ax, positions, distances, estimated_position):
    ax.clear()

    # Create a grid for plotting spheres
    u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
    x = np.cos(u) * np.sin(v)
    y = np.sin(u) * np.sin(v)
    z = np.cos(v)

    # Plot spheres based on distances
    for (pos, dist) in zip(positions, distances):
        ax.plot_surface(pos[0] + dist * x, pos[1] + dist * y, pos[2] + dist * z, color='b', alpha=0.1)

    # Plot estimated position
    ax.scatter(*estimated_position, color='r', s=100, label='Estimated Position')

    # Plot specific Cartesian point (10, 10, 0)
    specific_point = (10, 10, 0)
    ax.scatter(*specific_point, color='g', s=100, label='Specific Point (10, 10, 0)')

    # Set axis labels
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.legend()

    # Set grid and limits for better visibility
    ax.grid(True)
    ax.set_xlim([0, 10])
    ax.set_ylim([0, 10])
    ax.set_zlim([0, 10])

def start_server():
    s = socket.socket()
    s.bind(('0.0.0.0', 8080))
    s.listen(5)
    print('Server listening on port 8080...')

    client_id = 0
    while True:
        c, addr = s.accept()
        print(f"Connected with {addr}")
        client_thread = threading.Thread(target=handle_client_connection, args=(c, client_id))
        client_thread.start()
        client_id += 1

if __name__ == "__main__":
    plot_thread = threading.Thread(target=plot_in_main_thread, daemon=True)
    plot_thread.start()
    start_server()
