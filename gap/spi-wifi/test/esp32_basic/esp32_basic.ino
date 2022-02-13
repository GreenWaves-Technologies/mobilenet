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

//#include "SPISlave.h"
//#include <ESP8266WiFi.h>
#include <WiFi.h>
#include <WiFiClient.h>
#include <WiFiUdp.h>

WiFiClient tcpClient;

#define L 1460
uint8_t data[L];
unsigned long start;

void setup() {
  Serial.begin(115200);
  Serial.println("Start");

  Serial.println("Connecting...\n");
  WiFi.mode(WIFI_STA);
  WiFi.begin("TP-Link_0234", "56807325"); //WIFI SSID and Password
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("Connected to WiFi AP successful!");

  Serial.println("Connecting to TCP Socket...");
  const uint16_t port = 80;
  const char *host = "192.168.0.145";
  while (!tcpClient.connect(host, port)) {
    Serial.println("TCP Connection to host failed");
    delay(500);
  }
  delay(500);
  Serial.println("Connected to server successful!");
  //tcpClient.setNoDelay(1);
  //tcpClient.setSync(1);

  for(int i; i<L; i++){
    data[i]=(uint8_t) i;
  }

  /*
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
  */

}

void loop() {

    start = millis();
    for(int i=0; i<1000; i++){

      if(tcpClient.connected()){
        data[0] = (uint8_t) i;
        int written = tcpClient.write(data, L);
        yield();
        if(written<L){
          Serial.println("Failed to write");
          Serial.println(written);
        }
      }
      else{
        Serial.println("Server connection lost. Stopping.");
        exit(0);
      }
    }
    tcpClient.flush();
    Serial.println(millis()-start);
    delay(500);
    tcpClient.stop();
    exit(0);
  
  }
