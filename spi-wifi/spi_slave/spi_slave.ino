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

//CRC8 Global Variables
//#define DI 0x07
//static unsigned char crc8Table[256];

const uint16_t port = 8584;
const char *host = "192.168.0.245";
//const char *host = "192.168.0.145";


//const char *ssid = "TP-Link_0234";
//const char *pass = "56807325";

const char *ssid = "TP-Link_D0D4";
const char *pass = "QxamQJdv8j";

volatile bool interrupted = false;

static uint32_t lowbit = 5;
static uint32_t highbit = 4;

static uint8_t indexes = 0;

#define BUFFERSIZE (4000)
//#define BUFFERSIZE (1500)
static uint8_t tcpBuffer[BUFFERSIZE];
static uint8_t packetBuffer[32];
volatile int bufferLength = 0;
volatile int packetLength = 0;

#define PACKET_TO_TRANSMIT 125
//#define PACKET_TO_TRANSMIT 50
volatile uint8_t totalPacketToTransmit = 0;

//Command received from servers/clouds
static uint8_t commands[4];

WiFiClient tcpClient;

void setup() {
    Serial.begin(115200);
    Serial.println("Start");

    pinMode(lowbit, OUTPUT);
    pinMode(highbit, OUTPUT);

    digitalWrite(highbit, LOW);
    digitalWrite(lowbit, LOW);

    //Connect to WIFI
    Serial.println("Connecting...\n");
    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, pass); //WIFI SSID and Password
    while (WiFi.status() != WL_CONNECTED)
    {
        delay(500);
        Serial.print(".");
    }
    Serial.println("Connected to WiFi AP successful!");
    
    //Connect to Server Socket
    Serial.println("Connect to TCP Socket");
    while(!tcpClient.connect(host, port)) {
        Serial.println("TCP Connection to host failed");
        delay(500);
    }
    Serial.println("Connected to server successful!");

    SPISlave.onData([](uint8_t * data, size_t len) {
        //for (int i = 0; i < len; i++) {
        //  Serial.print(data[i]);
        //  Serial.print(" ");
        //}
        //Serial.println("");
        digitalWrite(highbit, LOW);
        digitalWrite(lowbit, LOW);
        memcpy((uint8_t *)packetBuffer, data, 32);
        interrupted = true;
        
    });

    SPI1C2 |= 1 << SPIC2MISODM_S;
    SPISlave.setStatus(0xFAFBFCFD);
    SPISlave.begin(4);
}

static unsigned long prev_time = 0;
static unsigned long cur_time = 0;

void loop() {
    if(interrupted) {
        if(indexes == 25) {
            indexes = 0;
        }

        if(packetBuffer[1] < indexes) {
            digitalWrite(highbit, LOW);
            digitalWrite(lowbit, HIGH);
            interrupted = false;
            return;
        } else if(packetBuffer[1] > indexes) {
            digitalWrite(highbit, HIGH);
            digitalWrite(lowbit, LOW);
            interrupted = false;
            return;
        }

        packetLength = (uint32_t)packetBuffer[0];

        memcpy(tcpBuffer + bufferLength, packetBuffer + 2, packetLength);
        bufferLength += packetLength;
        totalPacketToTransmit += 1;

        if(totalPacketToTransmit == PACKET_TO_TRANSMIT) {
            if(tcpClient.connected()) {
                while(tcpClient.availableForWrite() < bufferLength) {
                    delay(0);
                }
                tcpClient.write(tcpBuffer, bufferLength);
            }
            if(tcpClient.connected() && tcpClient.available()) {
                for(int i = 0; i < 4; i++) {
                    commands[i] = tcpClient.read();
                }
                uint32_t commandStatus = commands[0] | (commands[1] << 8) | (commands[2] << 16) | (commands[3] << 24);
                SPISlave.setStatus(commandStatus);
            }
            
            bufferLength = 0;
            totalPacketToTransmit = 0;
        }

        indexes += 1;
        interrupted = false;

        digitalWrite(highbit, LOW);
        digitalWrite(lowbit, HIGH);
    }
}
