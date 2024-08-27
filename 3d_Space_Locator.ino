#include <Arduino.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>

#define SERVICE_UUID        "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
#define CHARACTERISTIC_UUID "beb5483f-36e1-4688-b7f5-ea07361b26a8"

BLEServer *pServer = NULL;
BLECharacteristic *pCharacteristic = NULL;
bool deviceConnected = false;

float calculateDistance(int); 

class MyServerCallbacks : public BLEServerCallbacks {
  void onConnect(BLEServer* pServer) {
    deviceConnected = true;
    Serial.println("Device connected");
  }

  void onDisconnect(BLEServer* pServer) {
    deviceConnected = false;
    Serial.println("Device disconnected");
  }
};

class MyCallbacks : public BLECharacteristicCallbacks {
  void onWrite(BLECharacteristic *pCharacteristic) {
    String value = pCharacteristic->getValue().c_str();  // Get the value as Arduino String

    // Process the received value
    Serial.print("Received value from phone: ");
    Serial.println(value);

    // Convert the received value to an integer (assuming it's a valid dBm value)
    int rssi;
    if (value.toInt() != 0) {
      rssi = value.toInt();
      Serial.print("Parsed RSSI value: ");
      Serial.println(rssi);
      Serial.print("Distnace : ");
      Serial.println(calculateDistance(rssi));
      // Process the RSSI value as needed for your application
    }
    //  else {
    //   Serial.println("Invalid RSSI value received.");
    }
    if (value == "GET_RSSI") {
      int simulatedRSSI1 = -50;  // Simulated RSSI for the first ESP32
      int simulatedRSSI2 = -55;  // Simulated RSSI for the second ESP32
      
      float distance1 = calculateDistance(simulatedRSSI1);
      float distance2 = calculateDistance(simulatedRSSI2);
      
      Serial.print("Simulated RSSI 1: "); Serial.println(simulatedRSSI1);
      Serial.print("Calculated Distance 1: "); Serial.println(distance1);
      Serial.print("Simulated RSSI 2: "); Serial.println(simulatedRSSI2);
      Serial.print("Calculated Distance 2: "); Serial.println(distance2);
      
      // Respond with simulated RSSI values
      String response = "RSSI1:" + String(simulatedRSSI1) + " RSSI2:" + String(simulatedRSSI2);
      pCharacteristic->setValue(response);
      pCharacteristic->notify();
    }
  }
};


float calculateDistance(int rssi) {
    const float A = -69;  // RSSI at 1 meter
    const float n = 2.0;  // Path loss exponent
    return pow(10, (A - rssi) / (10 * n));
}

void setup() {
  Serial.begin(115200);
  BLEDevice::init("ESP32_Sphere_1");

  BLEServer *pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());
  
  BLEService *pService = pServer->createService(SERVICE_UUID);
  
  BLECharacteristic *pCharacteristic = pService->createCharacteristic(
    CHARACTERISTIC_UUID,
    BLECharacteristic::PROPERTY_WRITE
  );
  pCharacteristic->setCallbacks(new MyCallbacks());
  
  pService->start();
  BLEAdvertising *pAdvertising = pServer->getAdvertising();
  pAdvertising->start();
  
  Serial.println("Waiting for client connection");
}

void loop() {
}
