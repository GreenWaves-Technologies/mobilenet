#ifndef __SPI_WIFI_H__
#define __SPI_WIFI_H__

#include "pmsis.h"

extern uint8_t spi_tx_buffer[34] __attribute__((aligned(4))); // alignment is a requirement for SPI
extern uint8_t spi_rx_cmd_buffer[5] __attribute__((aligned(4)));
extern uint8_t spi_rx_buffer[5] __attribute__((aligned(4)));

#define SPI_PACKET_LENGTH (34)
#define SPI_DATA_LENGTH (30)
#define SPI_RX_LENGTH (5)

#define TCP_PACKET_LENGTH (730)
#define TCP_DATA_LENGTH (726)

#define DI 0x07

extern RT_L2_DATA uint8_t packet[TCP_PACKET_LENGTH];
extern uint32_t dataPos;

extern RT_L2_DATA uint8_t commands[4];

extern struct pi_device spi_dev;
extern struct pi_device gpio_lowbit;
extern struct pi_device gpio_highbit;
extern pi_gpio_e gpio_in_highbit, gpio_in_lowbit;
extern uint32_t v_lowbit, v_highbit;

extern unsigned char crc8Table[256];     /* 8-bit table */

extern int initializeSPI();
extern void transmitSPI(uint8_t * data, int dataLength, int kind);
extern void initCrc8();
extern uint8_t crc8(uint8_t * byteArray, int start, int end);
#endif
