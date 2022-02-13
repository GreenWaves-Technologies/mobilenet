## Wire Connections:
|GAP8|ESP8266|Functions|
|---|---|---|
|14|GND|GND|
|13|D5|SCLK|
|12|D6|MISO|
|11|D7|MOSI|
|10|D8|CS|
|9|D1|GPIO_LOW_BIT|
|8|D2|GPIO_HIGH_BIT|

![](.\figures\wire_connections.jpeg)

## Packet Protocol
### SPI TX
34 bytes packet
```
 ---------------------------------------
| Commands(2B)| Length(1B) | Index (1B) |
 ---------------------------------------
| Data (up to 30 byte)                  |
 ---------------------------------------
```
### SPI Status RX
5 bytes packet
```
 ---------------------------------------
| Commands(1B)                          |
 ---------------------------------------
| Data (up to 4 byte)                   |
 ---------------------------------------
```
used to transmit commands including: `include_img`, `num_feats` or `refresh`. This data is updated every time `transmitSPI` is triggered and the results are stored in the array `commands[4]`.

### Data Packet
730 bytes data packet
```
 ---------------------------------------
| Kind(1B)| Index(1B) | Length (2B)     |
 ---------------------------------------
| Data (up to 726 byte)                 |
 ---------------------------------------
```
`Kind` is either `0` or `1` to determine packet is the image or feature. `Index` used to form the data in the server. 

## Usage
### GAP8
`initializeSPI` used to initialize SPI interface and GPIOs. 
`transmitSPI(uint8_t * data, int dataLength, int kind)` is used to transmit data with specified length and kind.

Include `spi_wifi.h` and `spi_wifi.c` to use the two functions.

### Arduino/ESP8266 - lwip2

*Recompile* lwip. 

In order to achieve better wifi performance, three parameters in `lwip` is modified. The location is `Arduino/hardware/esp8266/esp8266/tools/sdk/lwip2/builder/glue-lwip/arduino/lwipopts.h`

`TCP_SND_BUF` to `(8 * TCP_MSS)`

`TCP_SND_QUEUELEN` to `16`

`PBUF_POOL_BUFSIZE` to `2048`

recompile at `Arduino/hardware/esp8266/esp8266/tools/sdk/lwip2/`
```
make
```
might need to comment some lines in Makefile to make sure that it does not get new files and revert the changes.

Make sure the changes take place in the file `Arduino/hardware/esp8266/esp8266/tools/sdk/lwip2/include/lwipopts.h`.

### Arduino/ESP8266 - Parameters
CPU Frequency : 160Mhz
LwIP Variant: V2 high bandwidths


## Current Perf
220 - 380 KBps with good network; 120 - 220 KBps with bad network. 

42 us for 34 bytes SPI transmit
~30 us for SPISlave.onData get triggered
other latency come from synchronized TCP write calls

WiFi could achieve ~1.5 MBps.