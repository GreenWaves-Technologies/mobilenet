
#include "pmsis.h"

static uint8_t spi_tx_buffer[32] __attribute__((aligned(32))); // alignment is a requirement for SPI
static uint8_t spi_cmd_buffer[32] __attribute__((aligned(32)));
static uint8_t spi_status_buffer[32] __attribute__((aligned(32)));
static uint8_t spi_zeros[32] __attribute__((aligned(32)));
static uint8_t spi_read_status[32] __attribute__((aligned(32)));

// #define DEBUG

#define DI 0x07
static unsigned char crc8Table[256];     /* 8-bit table */
static uint8_t isRefresh = 0x00;
static uint8_t includeImage = 0x00;
static uint8_t numFeats = 8;

/*
* Should be called before any other crc function.  
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
#ifdef DEBUG
        printf("table[%d] = %d (0x%X)\n", i, crc, crc);
#endif
    }
}

/*
* For a byte array whose accumulated crc value is stored in *crc, computes
* resultant crc obtained by appending m to the byte array
*/
uint8_t crc8(uint8_t * byteArray, int start, int end) {   
    uint8_t crc = 0x00;
    for(int i = start; i < end; i++) {
        crc = crc8Table[crc ^ byteArray[i]];
#ifdef DEBUG
        printf("%x:%x ", byteArray[i], crc);
#endif
    }
#ifdef DEBUG
    printf("\n");
#endif
    return crc;
}

void test_spi_master()
{
    printf("SPI example start\n");

    struct pi_spi_conf spi_conf = { 0 };
    struct pi_device spi_dev = { 0 };

    pi_spi_conf_init(&spi_conf);
    spi_conf.max_baudrate = 8 * 1000 * 1000;
    spi_conf.itf = 1; // on Gapuino SPI1 can be used freely
    spi_conf.cs = 0;
    spi_conf.wordsize = PI_SPI_WORDSIZE_8;
    spi_conf.polarity = PI_SPI_POLARITY_0;
    spi_conf.phase = PI_SPI_PHASE_0;

    pi_open_from_conf(&spi_dev, &spi_conf);

    if (pi_spi_open(&spi_dev)) {
        printf("SPI open failed\n");
        pmsis_exit(-1);
    }

    spi_cmd_buffer[0] = 0x02;
    spi_cmd_buffer[1] = 0x00;

    spi_status_buffer[0] = 0x04;
    spi_status_buffer[1] = 0x00;
    for (int i = 0; i < 32; i++) {
        spi_zeros[i] = 0;
        spi_read_status[i] = 0;
    }

    initCrc8();
    

//#define SYNC

    const size_t loops = 1000;
    for (uint8_t i = 0; i < loops; i += 1) {
        
        for (size_t j = 2; j < 32; j += 1) {
            
            spi_tx_buffer[j] = 0x00 + j + i;
        }
        spi_tx_buffer[0] = 30;
        spi_tx_buffer[1] = crc8(spi_tx_buffer, 2, 32);

#ifdef DEBUG
        for(int j = 0; j < 32; j++) {
            printf("%x ", spi_tx_buffer[j]);
        }
#endif
        // printf("\n");
        // printf("SPI send (%i/%i), size: %i\n", i + 1, loops, sizeof(spi_tx_buffer));

        // use pi_spi_send to only send data, pi_spi_receive to only receive data and pi_spi_transfer to send and receive data

// #ifdef SYNC
        do {
            spi_read_status[0] = 0x00;

            pi_spi_send(&spi_dev, spi_cmd_buffer, 8 * 2, PI_SPI_CS_KEEP | PI_SPI_LINES_SINGLE);
            pi_spi_send(&spi_dev, spi_tx_buffer, 8 * 32, PI_SPI_CS_KEEP | PI_SPI_LINES_SINGLE);
            pi_time_wait_us(100);
// #else
//         pi_task_t wait_task = { 0 };
//         pi_task_block(&wait_task);
//         pi_spi_send_async(&spi_dev, spi_tx_buffer, 8 * sizeof(spi_tx_buffer), PI_SPI_CS_KEEP | PI_SPI_LINES_SINGLE, &wait_task);
//         pi_task_wait_on(&wait_task);
// #endif
            do {
                pi_spi_send(&spi_dev, spi_status_buffer, 8 * 1, PI_SPI_CS_KEEP | PI_SPI_LINES_SINGLE);
#ifdef DEBUG
                for (size_t j = 0; j < 1; j += 1) {
                    printf("%x ", spi_status_buffer[j]);
                }
                printf("\n");
#endif
                pi_spi_transfer(&spi_dev, spi_zeros, spi_read_status, 8 * 4, PI_SPI_CS_KEEP | PI_SPI_LINES_SINGLE);
// #ifdef DEBUG
                for (size_t j = 0; j < 4; j += 1) {
                    printf("%x ", spi_read_status[j]);
                }
                printf("\n");
// #endif
                pi_time_wait_us(100);
            } while(spi_read_status[0] == 0x00);
            pi_time_wait_us(100);
        } while (spi_read_status[0] == 0x02);

        if(spi_read_status[0] == 0x03) {

        }
    }

    printf("SPI example end\n");

    pmsis_exit(0);
}

int main(void)
{
    printf("\n\n\t *** PMSIS SPI Master ***\n\n");
    return pmsis_kickoff((void *) test_spi_master);
}
