# TriBLE Locator

A project which can be used as an alternative to locate yourself in an open environment where gps is not available using 3 esp32's.
1st project is using a 3rd party mobile app "nRF Connect" to send rssi data sequentially to each esp32 and get the location of mobile using trilateration and plot it using matplotlib.
2nd project using the server laptop as the main device to locate which tracks the rssi data of each esp32 and computes it on the server file and plot it using matlplotlib which updates itself every 4 seconds according to the server laptop's position which could be relative or absolute to each esp32.    
