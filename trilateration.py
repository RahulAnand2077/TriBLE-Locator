import numpy as np
from scipy.optimize import least_squares

# Define the known positions of the ESP32 devices
positions = np.array([
    [0, 0, 0],   # Position of the first ESP32
    [1, 0, 0],   # Position of the second ESP32
    [0, 1, 0]    # Position of the third ESP32
])

# Distances from each ESP32 (in meters), obtained from RSSI
distances = np.array([0.5, 0.6, 0.7])

def trilateration(positions, distances):
    def equations(p):
        x, y, z = p
        return np.sqrt((x - positions[0][0])**2 + (y - positions[0][1])**2 + (z - positions[0][2])**2) - distances[0], \
               np.sqrt((x - positions[1][0])**2 + (y - positions[1][1])**2 + (z - positions[1][2])**2) - distances[1], \
               np.sqrt((x - positions[2][0])**2 + (y - positions[2][1])**2 + (z - positions[2][2])**2) - distances[2]

    initial_guess = np.mean(positions, axis=0)
    result = least_squares(equations, initial_guess)
    return result.x

# Calculate the estimated position
estimated_position = trilateration(positions, distances)
print("Estimated Position:", estimated_position)


import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Line3DCollection

def plot_spheres(positions, distances):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Plot spheres
    u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
    x = np.cos(u) * np.sin(v)
    y = np.sin(u) * np.sin(v)
    z = np.cos(v)
    
    for (pos, dist) in zip(positions, distances):
        ax.plot_surface(pos[0] + dist*x, pos[1] + dist*y, pos[2] + dist*z, color='b', alpha=0.1)

    # Plot the estimated position
    ax.scatter(*estimated_position, color='r', s=100, label='Estimated Position')

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    plt.legend()
    plt.show()

plot_spheres(positions, distances)
