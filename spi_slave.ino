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

#define DEBUG 0

//CRC8 Global Variables
#define DI 0x07
static unsigned char crc8Table[256];

//TCP Buffers
#define BUFFERSIZE 1000
static uint8_t tcpBuffer[BUFFERSIZE];
static int bufferLength = 0;

//Command received from servers/clouds
static uint8_t commands[4];

// Status: there are total 4 status:
// Processing(0x00): received 32 bytes data are under processing
// - GAP8 will be in loop to acquire new status
// ACK(0x01): OK
// ReTransmit(0x02): checksum(CRC8) is not correct
// - GAP8 will need retransmit the current 32 bytes
// Command(0x03): receive new commands from cloud
// - GAP8 should receive new commands and update its value


//WiFi Client
WiFiClient tcpClient;
WiFiUDP udpClient;
#define TCP


/*
* Should be called before any other crc function.  
* Setup the crctable
*/
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

    //Initialize CRC table
    initCrc8();
    
    //Connect to WIFI
    Serial.println("Connecting...\n");
    WiFi.mode(WIFI_STA);
    WiFi.begin("APT27", "ABCabc123##"); //WIFI SSID and Password
    while (WiFi.status() != WL_CONNECTED)
    {
        delay(500);
        Serial.print(".");
    }
    Serial.println("Connected to WiFi AP successful!");
    
    //Connect to Server Socket
    const uint16_t port = 8585;
    const char *host = "192.168.0.215";

#ifdef TCP
    Serial.println("Connect to TCP Socket");
    while(!tcpClient.connect(host, port)) {
        Serial.println("TCP Connection to host failed");
        delay(500);
    }
    Serial.println("Connected to server successful!");
    tcpClient.setNoDelay(1);
    tcpClient.setSync(1);
#else
    Serial.println("Connect to UDP Socket");
    while(!udpClient.beginPacket(host, port)) {
        Serial.println("UDP Connection to host failed");
        delay(500);
    }
    Serial.println("UDP Connected to server successful!");
#endif
    

  // data has been received from the master. Beware that len is always 32
  // and the buffer is autofilled with zeroes if data is less than 32 bytes long
  // It's up to the user to implement protocol for handling data length
    SPISlave.onData([](uint8_t * data, size_t len) {
#if DEBUG
        for(int i = 0; i < 32; i++) {
            Serial.print(data[i], HEX);
            Serial.print(" ");
        }
        Serial.println("");
#endif
        SPISlave.setStatus(0x00);
        // Serial.println("Data Received");

        uint8_t crc = crc8(data, 2, 32);
#if DEBUG
        Serial.println(crc, HEX);
#endif
        if(crc != data[1]) {
            SPISlave.setStatus(0x02);
            return;
        }

#if DEBUG
        Serial.println("Data Received!");
        Serial.printf("Data Avail:%d\n", tcpClient.availableForWrite());
#endif
        int packetLength = (int)data[0];
        if(packetLength + bufferLength < BUFFERSIZE) {
            memcpy(tcpBuffer + bufferLength, data + 2, (int)data[0]);
            bufferLength += packetLength;
        } else {
            int transmitLength = BUFFERSIZE - bufferLength;
            memcpy(tcpBuffer + bufferLength, data + 2, transmitLength);

#if DEBUG
            for(int i = 0; i < sizeof(tcpBuffer); i++) {
                Serial.printf("%d ", tcpBuffer[i]);
            }
            Serial.println("");
#endif

#ifdef TCP
            Serial.println("TCP Transmission Started");
            while(tcpClient.availableForWrite() < BUFFERSIZE) {
                delay(1);
            }
            Serial.printf("Data Avail:%d\n", tcpClient.availableForWrite());
            tcpClient.write(tcpBuffer, BUFFERSIZE);
            tcpClient.flush();
            Serial.println("TCP Transmission Finished");

            if(tcpClient.available()) {
                for(int i = 0; i < 4; i++) {
                    commands[i] = tcpClient.read();
                }
            }

            for(int i = 0; i < 4; i++) {
                Serial.printf("%d ", commands[i]);
            }
            Serial.println("");
#else
            Serial.println("UDP Transmission Started");
            udpClient.write(tcpBuffer, BUFFERSIZE);
            Serial.println("UDP Transmission Finished");
#endif
            
            memset(tcpBuffer, 0, sizeof(tcpBuffer));
            memcpy(tcpBuffer, data + 2 + transmitLength, data[0] - transmitLength);
            bufferLength = data[0] - transmitLength;
        }

        if(commands[0] == 0x01) {
            // uint8_t statusNew = commands[3] | commands[2] << 4 | commands[1] << 5 | commands[0] << 7;
            uint32_t statusNew = 0x03;
            for(int i = 1; i < 4; i++) {
                statusNew <<= 8;
                statusNew |= (uint32_t)commands[i] & 0xff;
            }
            SPISlave.setStatus(statusNew);
            Serial.printf("Send Command: %d\n", statusNew);
            memset(commands, 0, sizeof(commands));
        } else {
            SPISlave.setStatus(0x01);
        }
    });

  // The master has read out outgoing data buffer
  // that buffer can be set with SPISlave.setData
    SPISlave.onDataSent([]() {
#if DEBUG
        Serial.println("Answer Sent");
#endif
    });

    // status has been received from the master.
    // The status register is a special register that bot the slave and the master can write to and read from.
    // Can be used to exchange small data or status information
    SPISlave.onStatus([](uint32_t data) {
        Serial.printf("Status: %u\n", data);
    });

    // The master has read the status register
    SPISlave.onStatusSent([]() {
    // Serial.println("Status Sent");
    });
    // Setup SPI Slave registers and pins
    SPISlave.begin();
  //  
    SPI1C2 |= 1 << SPIC2MISODM_S;
    SPISlave.setStatus(0x01);

}

void loop() {}
