#include "spi_wifi.h"

#define SPI_FREQ (9 * 1000 * 1000)

// alignment is a requirement for SPI
uint8_t spi_tx_buffer[SPI_PACKET_LENGTH] __attribute__((aligned(4))) = {0}; 
uint8_t spi_rx_cmd_buffer[SPI_RX_LENGTH] __attribute__((aligned(4))) = {0};
uint8_t spi_rx_buffer[SPI_RX_LENGTH] __attribute__((aligned(4))) = {0};

RT_L2_DATA uint8_t packet[TCP_PACKET_LENGTH] = { 0 };
uint32_t dataPos = 0;

RT_L2_DATA uint8_t commands[4] = { 0 };

struct pi_device spi_dev = { 0 };
struct pi_device gpio_lowbit = { 0 };
struct pi_device gpio_highbit = { 0 };

pi_gpio_e gpio_in_lowbit = PI_GPIO_A19_PAD_33_B12;
pi_gpio_e gpio_in_highbit = PI_GPIO_A5_PAD_17_B40;
uint32_t v_lowbit = 0, v_highbit = 0;
unsigned char crc8Table[256];     /* 8-bit table */
/*
Initialize SPI and GPIOs
*/
int initializeSPI() {

    //Initialize SPI
    struct pi_spi_conf spi_conf = { 0 };

    pi_spi_conf_init(&spi_conf);
    spi_conf.max_baudrate = SPI_FREQ;
    spi_conf.itf = 1; // on Gapuino SPI1 can be used freely
    spi_conf.cs = 0;
    spi_conf.wordsize = PI_SPI_WORDSIZE_8;
    spi_conf.polarity = PI_SPI_POLARITY_0;
    spi_conf.phase = PI_SPI_PHASE_0;

    pi_open_from_conf(&spi_dev, &spi_conf);

    if (pi_spi_open(&spi_dev)) {
        printf("SPI open failed\n");
        return -1;
    }

    // Initialize GPIO
    struct pi_gpio_conf gpio_conf;
    pi_gpio_conf_init(&gpio_conf);
    pi_open_from_conf(&gpio_lowbit, &gpio_conf);
    pi_open_from_conf(&gpio_highbit, &gpio_conf);
    if (pi_gpio_open(&gpio_lowbit) || pi_gpio_open(&gpio_highbit)) {
        printf("GPIO open failed\n");
        return -1;
    }

    pi_gpio_flags_e cfg_flags = PI_GPIO_INPUT; // PI_GPIO_INPUT|PI_GPIO_PULL_DISABLE|PI_GPIO_DRIVE_STRENGTH_LOW;
    pi_gpio_pin_configure(&gpio_lowbit, gpio_in_lowbit, cfg_flags);
    pi_gpio_pin_configure(&gpio_highbit, gpio_in_highbit, cfg_flags);

    // Set SPI Status RX Commands
    memset(spi_rx_cmd_buffer, 0, 5);
    memset(spi_rx_buffer, 0, 5);
    spi_rx_cmd_buffer[0] = 0x04;

    return 0;
}

/*
Get SPI Status
The array commands will bet set with the new received status.
*/
void spiGetStatus() {
    // transfer cmd 0x04 to get up to 4 Bytes status
    pi_spi_transfer(&spi_dev, spi_rx_cmd_buffer, spi_rx_buffer, 8 * 5, PI_SPI_CS_KEEP | PI_SPI_LINES_SINGLE);
    // for (size_t j = 0; j < 5; j += 1) {
    //     printf("%x %x\n", spi_rx_cmd_buffer[j], spi_rx_buffer[j]);
    // }
    memcpy(commands, spi_rx_buffer + 1, 4);
}

/* 
Form Data into TCP Packet
Each Packet is fixed-length 730 Bytes with 4 Bytes head.
The head is Kind(1 Byte), Index(1 Byte), Length(2 Bytes)
Kind: 0 or 1, 0 is image and 1 is feature
Index: 0 - 255
Length: 0 - 726 
*/
void formTCPPacket(uint8_t * packet, uint8_t * data, int dataLength, uint8_t kind, uint8_t index) {

    //Calculate Packet Length
    uint16_t packetLength = 0;
    uint32_t startPos = TCP_DATA_LENGTH * index;
    if(TCP_DATA_LENGTH * (index + 1) < dataLength) {
        packetLength = TCP_DATA_LENGTH;
    } else {
        packetLength = dataLength - startPos;
    }

    memset(packet, 0, TCP_PACKET_LENGTH);

    packet[0] = kind;
    packet[1] = index;
    packet[2] = (uint8_t)(packetLength >> 8) & 0XFF;
    packet[3] = (uint8_t)(packetLength & 0xFF);

    memcpy(packet + 4, data + startPos, packetLength);
}

/*
Form SPI Packet from TCP Packet
Each SPI Packet is 34 bytes with 2 bytes commands and 2 bytes head;
The command(2 Bytes): 0x02 0x00 are used to send data;
The head is Length(1 Bytes), Index(1 Bytes);
*/
void formSPIPacket(uint8_t * packet, uint8_t * data, int dataLength, uint8_t index) {
    //calculate packet length
    uint8_t packetLength = 0;
    uint32_t startPos = SPI_DATA_LENGTH * index;
    if(SPI_DATA_LENGTH * (index + 1) < dataLength) {
        packetLength = SPI_DATA_LENGTH;
    } else {
        packetLength = dataLength - startPos;
    }

    memset(spi_tx_buffer, 0, SPI_PACKET_LENGTH);

    spi_tx_buffer[0] = 0x02;
    spi_tx_buffer[1] = 0x00;
    spi_tx_buffer[2] = packetLength;
    spi_tx_buffer[3] = index;
    memcpy(packet + 4, data + startPos, packetLength);
}

/*
Transmit SPI Packets.
GPIOs are used to acknowledge the received data.
status(2-bit): 
0x00 - still processing
0x01 - OK
0x02 - packet with higher index being transmitted
*/
uint8_t spiSendPacket(uint8_t * spi_tx_buffer, int dataLength) {
    uint8_t status = 0x00;
    // uint32_t start_time = rt_time_get_us();
    // spi_read_status[0] = 0x00;
    status = 0x00;

    pi_spi_send(&spi_dev, spi_tx_buffer, 8 * dataLength, PI_SPI_CS_KEEP | PI_SPI_LINES_SINGLE);
    // 30 us seems to be the minimal waiting time to wait for the interrupts of SPI being called
    // slower than 30 us might lead to the wrong GPIO read and wrong status.
    pi_time_wait_us(30);

    do {
        pi_gpio_pin_read(&gpio_lowbit, gpio_in_lowbit, &v_lowbit);
        pi_gpio_pin_read(&gpio_highbit, gpio_in_highbit, &v_highbit);
        status = v_highbit << 1 | v_lowbit;
        // printf("HIGH: %d | LOW: %d | status: %d\n", v_highbit, v_lowbit, status);
        status = v_highbit << 1 | v_lowbit;
    } while (status == 0x00);

    return status;
}

void transmitSPI(uint8_t * data, int dataLength, int kind) {

    uint8_t indexTCP = 0;
    uint8_t indexSPI = 0;
    uint8_t status = 0x00;
    uint8_t totalPacketTCP = 0;
    uint8_t totalPacketSPI = 0;

    // totalPacketTCP = AT_INPUT_SIZE / TCP_DATA_LENGTH + 1;
    totalPacketTCP = dataLength / TCP_DATA_LENGTH + 1;
    while(indexTCP < totalPacketTCP) {
        formTCPPacket(packet, data, dataLength, kind, indexTCP);
        indexTCP++;

        indexSPI = 0;
        totalPacketSPI = TCP_DATA_LENGTH / SPI_DATA_LENGTH + 1;
        
        while(indexSPI < totalPacketSPI) {
            formSPIPacket(spi_tx_buffer, packet, TCP_PACKET_LENGTH, indexSPI);

            status = spiSendPacket(spi_tx_buffer, SPI_PACKET_LENGTH);
            // printf("Index: %d %d\n\n", spi_tx_buffer[3], status);
            if(status == 0x01) {
                indexSPI += 1;
            } else if(status == 0x02) {
                indexSPI = indexSPI == 0? 0: indexSPI - 1;
            } else {
                indexSPI += 1;
            }
        }

    }

    spiGetStatus();
}

void initCrc8() {
    int i,j;
    unsigned char crc;

    for (i=0; i<256; i++) {
        crc = i;
        for (j=0; j<8; j++) {
            crc = (crc << 1) ^ ((crc & 0x80) ? DI : 0);
        }
        crc8Table[i] = crc & 0xFF;
    }
}

uint8_t crc8(uint8_t * byteArray, int start, int end) {   
    uint8_t crc = 0x00;
    for(int i = start; i < end; i++) {
        crc = crc8Table[crc ^ byteArray[i]];
    }
    return crc;
}

