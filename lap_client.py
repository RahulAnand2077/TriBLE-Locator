import asyncio
from bleak import BleakScanner
import socket

esp32_address1 = "08:B6:1F:B8:59:32"
esp32_address2 = "CC:7B:5C:A8:21:16"
esp32_address3 = "08:B6:1F:B8:76:12"

rssi = {}

async def scan():
    try:
        print("Starting scan...")
        scanner = BleakScanner()
        await scanner.start()
        await asyncio.sleep(10)  # Scan for 10 seconds
        await scanner.stop()

        devices = scanner.discovered_devices
        if devices:
            for device in devices:
                # Attempt to access RSSI directly
                rssi_value = device.rssi
                if device.address in {esp32_address1, esp32_address2, esp32_address3}:
                    if rssi_value is not None:
                        rssi[device.address] = rssi_value
        else:
            print("No devices found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def send_rssi_to_server(rssi_data):
    try:
        c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        c.connect(('192.168.1.52', 8080))  # Replace with your server IP and port
        print("Connected to server")

        # Format RSSI data as a list of values
        rssi_values = [str(value) for value in rssi_data.values()]
        rssi_message = '\n'.join(rssi_values) + '\n'
        
        print(f"Sending to server:\n{rssi_message.strip()}")
        c.sendall(rssi_message.encode('utf-8'))

        c.close()
    except socket.error as e:
        print(f"Socket error: {e}")

async def main():
    await scan()
    if rssi:
        send_rssi_to_server(rssi)

if __name__ == "__main__":
    asyncio.run(main())
