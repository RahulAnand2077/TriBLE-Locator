import serial
import time
import re

ser = serial.Serial('COM5', 115200, timeout=1)
time.sleep(2) 

rssi_pattern = re.compile(r"Parsed RSSI value: (-?\d+)")
distance_pattern = re.compile(r"Distance : ([\d\.]+)")

rssi_value = None
distance_value = None

def get_rssi_data():
    global rssi_value
    print(f"Fetching RSSI Data: {rssi_value}")
    return rssi_value

def get_distance_data():
    global distance_value
    print(f"Fetching Distance Data: {distance_value}")
    return distance_value


try:
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip()
            print(f"Received: {line}")

            rssi_match = rssi_pattern.search(line)
            distance_match = distance_pattern.search(line)

            if rssi_match:
                rssi_value = int(rssi_match.group(1))

            if distance_match:
                distance_value = float(distance_match.group(1))
        
except KeyboardInterrupt:
    print("Stopping the data extraction.")
finally:
    ser.close()
