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
const char *host = "192.168.0.215";

const char *ssid = "APT27";
const char *pass = "ABCabc123##";

volatile bool interrupted = false;

static uint32_t lowbit = 5;
static uint32_t highbit = 4;

static uint8_t indexes = 0;

#define BUFFERSIZE (4000)
static uint8_t tcpBuffer[BUFFERSIZE];
static uint8_t packetBuffer[32];
volatile int bufferLength = 0;
volatile int packetLength = 0;

#define PACKET_TO_TRANSMIT 125
volatile uint8_t totalPacketToTransmit = 0;

//Command received from servers/clouds
static uint8_t commands[4];

WiFiClient tcpClient;

static void initCrc8() {
    int i,j;
    unsigned char crc;

    for (i=0; i<256; i++) {
        crc = i;
        for (j=0; j<8; j++) {
            crc = (crc << 1) ^ ((crc & 0x80) ? DI : 0);
        }
        crc8Table[i] = crc & 0xFF;
#if DEBUG
        Serial.printf("table[%d] = %d (0x%X)\n", i, crc, crc);
#endif
    }
}

/*
* For a byte array whose accumulated crc value is calculated 
* byteArray is the input data, start/end are the indexes to be calculated
*/
uint8_t crc8(uint8_t * byteArray, int start, int end) {   
    uint8_t crc = 0x00;
    for(int i = start; i < end; i++) {
        crc = crc8Table[crc ^ byteArray[i]];
#if DEBUG
        Serial.printf("%x:%x ", byteArray[i], crc);
#endif
    }
#if DEBUG
    Serial.println("");
#endif
    return crc;
}


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

    // Does not use NoDelay or Sync, which degrades performance
//    tcpClient.setNoDelay(1);
//    tcpClient.setSync(1);

  // data has been received from the master. Beware that len is always 32
  // and the buffer is autofilled with zeroes if data is less than 32 bytes long
  // It's up to the user to implement protocol for handling data length
    SPISlave.onData([](uint8_t * data, size_t len) {
//        SPISlave.setStatus(0xFFFFFFFF);
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

//        unsigned long startTime = micros();
        if(indexes == 25) {
            indexes = 0;
        }
//      
        if(packetBuffer[1] < indexes) {
//            Serial.printf("Hit Duplicate Packet %d, %d\n", packetBuffer[1], indexes);
            digitalWrite(highbit, LOW);
            digitalWrite(lowbit, HIGH);
            interrupted = false;
            return;
        } else if(packetBuffer[1] > indexes) {
//            Serial.printf("Hit Larget Packet %d, %d\n", packetBuffer[1], indexes);
            digitalWrite(highbit, HIGH);
            digitalWrite(lowbit, LOW);
            interrupted = false;
            return;
        }

//        Serial.printf("Buffer Processed.\n");
        packetLength = (uint32_t)packetBuffer[0];

        memcpy(tcpBuffer + bufferLength, packetBuffer + 2, packetLength);
        bufferLength += packetLength;
        totalPacketToTransmit += 1;

        if(totalPacketToTransmit == PACKET_TO_TRANSMIT) {
    //        if(prev_time == 0) {
    //            prev_time = millis();
    //        } else {
    //            cur_time = millis();
    //            Serial.printf("SPI bandwidth: %.3f, %d, %d\n", (bufferLength / ((cur_time - prev_time) / 1000.0)), cur_time, prev_time);
    //            prev_time = cur_time;
    //        }
            if(tcpClient.connected()) {
    //            Serial.printf("Data Avail:%d\n", tcpClient.availableForWrite());
                while(tcpClient.availableForWrite() < bufferLength) {
                    delay(0);
                }
              
                tcpClient.write(tcpBuffer, bufferLength);
    //          Serial.println("TCP Transmission Finished");  
            }
    //
            if(tcpClient.connected() && tcpClient.available()) {
                for(int i = 0; i < 4; i++) {
                    commands[i] = tcpClient.read();
                }
//                Serial.printf("Commands: %x, %x, %x, %x\n", commands[0], commands[1], commands[2], commands[3]);
                uint32_t commandStatus = commands[0] | (commands[1] << 8) | (commands[2] << 16) | (commands[3] << 24);
                SPISlave.setStatus(commandStatus);
//                Serial.printf("Set New Status: %d\n", commandStatus);
            }
            
            bufferLength = 0;
            totalPacketToTransmit = 0;
//            unsigned long endTime = micros();
//            Serial.println(endTime - startTime);
        }

        indexes += 1;
        interrupted = false;

        digitalWrite(highbit, LOW);
        digitalWrite(lowbit, HIGH);
    }
}
