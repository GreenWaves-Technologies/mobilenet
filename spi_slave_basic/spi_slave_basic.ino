/*
    SPI Slave Demo Sketch
    Connect the SPI Master device to the following pins on the esp8266:

    GPIO    NodeMCU   Name  |   Uno
  ===================================
     15       D8       SS   |   D10
     13       D7      MOSI  |   D11
     12       D6      MISO  |   D12
     14       D5      SCK   |   D13

    Note: If the ESP is booting at a moment when the SPI Master has the Select line HIGH (deselected)
    the ESP8266 WILL FAIL to boot!
    See SPISlave_SafeMaster example for possible workaround

*/

#include "SPISlave.h"
#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <WiFiUdp.h>

WiFiClient tcpClient;

void setup() {
  Serial.begin(115200);
  Serial.println("Start");

  Serial.println("Connecting...\n");
  WiFi.mode(WIFI_STA);
  WiFi.begin("TP-Link_D0D4", "QxamQJdv8j"); //WIFI SSID and Password
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("Connected to WiFi AP successful!");

  Serial.println("Connecting to TCP Socket...");
  const uint16_t port = 80;
  const char *host = "192.168.0.245";
  while (!tcpClient.connect(host, port)) {
    Serial.println("TCP Connection to host failed");
    delay(500);
  }
  Serial.println("Connected to server successful!");
  tcpClient.setNoDelay(1);
  tcpClient.setSync(1);

  SPISlave.onData([](uint8_t* data, size_t len) {
    Serial.println("got " + String(len) + " bytes:");
    for (int i = 0; i < 32; i++) {
      Serial.print(data[i]);
      Serial.print(" ");
    }
    Serial.println("");

    SPISlave.setStatus(0x00);

    tcpClient.write(data, 32);
    tcpClient.flush();
    
    SPISlave.setStatus(0x01);
  });

  SPISlave.onDataSent([]() { });


  SPISlave.onStatus([](uint32_t data) { });

  SPISlave.onStatusSent([]() { });

  SPISlave.begin();
  SPI1C2 |= 1 << SPIC2MISODM_S;
  SPISlave.setStatus(0x01);

}

void loop() {}
