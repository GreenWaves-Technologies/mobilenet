/*
 * Copyright 2019 GreenWaves Technologies, SAS
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include "pmsis.h"
#include "bsp/flash/hyperflash.h"
#include "bsp/ram/hyperram.h"
#include "bsp/bsp.h"
#include "bsp/buffer.h"
#include "bsp/camera/himax.h"
#include "bsp/ram.h"
#include "bsp/display/ili9341.h"
#include "main.h"

#define BAUD 3000000
#define __XSTR(__s) __STR(__s)
#define __STR(__s) #__s
#define HIDDEN_WIDTH 28
#define HIDDEN_HEIGHT 28
#define HIDDEN_CHANNEL 32
#define SPATIAL_DIM (HIDDEN_WIDTH * HIDDEN_HEIGHT)
#define NUM_FEATS 	(HIDDEN_CHANNEL * SPATIAL_DIM)
#define AT_INPUT_SIZE 	(AT_INPUT_WIDTH*AT_INPUT_HEIGHT*AT_INPUT_COLORS)
#define NUM_PIXELS (AT_INPUT_WIDTH*AT_INPUT_HEIGHT)
#define CAMERA_WIDTH    (324)
#define CAMERA_HEIGHT   (244)
#define CAMERA_SIZE   	(CAMERA_HEIGHT*CAMERA_WIDTH)
#define EXTERNAL_RAM HyperRam
typedef signed char NETWORK_OUT_TYPE;

AT_HYPERFLASH_FS_EXT_ADDR_TYPE AT_L3_ADDR = 0;
L2_MEM NETWORK_OUT_TYPE *ResOut;
RT_L2_DATA uint32_t hist[256];
RT_L2_DATA uint32_t times[3];
RT_L2_DATA uint8_t Input_1[CAMERA_WIDTH*CAMERA_HEIGHT];
RT_L2_DATA uint8_t levels[256];
static pi_buffer_t buffer;
static pi_task_t task;
static uint8_t *rx_buffer;
struct pi_device camera;
struct pi_device uart;
struct pi_uart_conf uart_conf;
uint32_t start;
struct pi_device HyperRam;
struct pi_hyperram_conf hyper_conf;
static uint8_t spi_tx_buffer[32] __attribute__((aligned(32))); // alignment is a requirement for SPI
static uint8_t spi_cmd_buffer[32] __attribute__((aligned(32)));
static uint8_t spi_status_buffer[32] __attribute__((aligned(32)));
static uint8_t spi_zeros[32] __attribute__((aligned(32)));
static uint8_t spi_read_status[32] __attribute__((aligned(32)));
struct pi_spi_conf spi_conf = { 0 };
struct pi_device spi_dev = { 0 };
struct pi_device cluster_dev;
struct pi_cluster_conf conf;

void send_spi(uint8_t* buffer) {
    for (uint8_t i = 0; i < 32; i++) {
        spi_tx_buffer[i] = buffer[i];
    }
    pi_spi_send(&spi_dev, spi_cmd_buffer, 8 * 2, PI_SPI_CS_KEEP | PI_SPI_LINES_SINGLE);
    pi_spi_send(&spi_dev, spi_tx_buffer, 8 * 32, PI_SPI_CS_KEEP | PI_SPI_LINES_SINGLE);
    pi_time_wait_us(100);
    
    while (spi_read_status[0] == 0x00) {
        pi_spi_send(&spi_dev, spi_status_buffer, 8 * 1, PI_SPI_CS_KEEP | PI_SPI_LINES_SINGLE);
        pi_spi_transfer(&spi_dev, spi_zeros, spi_read_status, 8 * 4, PI_SPI_CS_KEEP | PI_SPI_LINES_SINGLE);
        /*printf("status: ");*/
        /*for (size_t j = 0; j < 4; j += 1) {*/
            /*printf("%x ", spi_read_status[j]);*/
        /*}*/
        /*printf("\n");*/
        pi_time_wait_us(100);
    }
}

void open_spi() {
    pi_spi_conf_init(&spi_conf);
    spi_conf.max_baudrate = 5 * 1000 * 1000;
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
}

void open_uart() {
    pi_uart_conf_init(&uart_conf);
    uart_conf.baudrate_bps = BAUD;
    uart_conf.uart_id = 0;
    uart_conf.enable_tx = 1;
    uart_conf.enable_rx = 1;
    pi_open_from_conf(&uart, &uart_conf);
    if (pi_uart_open(&uart)) {
        printf("uart open failed\n");
    } else {
    	printf("uart open\n");
    }
}


void uart_read() {
	pi_pad_set_function(PI_PAD_46_B7_SPIM0_SCK, PI_PAD_FUNC0);
    rx_buffer = (uint8_t *) pmsis_l2_malloc((uint32_t) 2);
    pi_task_t wait_task = {0};
    pi_task_block(&wait_task);
    //printf("tasK_block passed\n");
    pi_uart_read_async(&uart, rx_buffer, 2, &wait_task);
    //printf("pi_uart_async_read called, waiting\n");
    pi_task_wait_on(&wait_task);
    printf("waiting over, got 1 byte with value %d\n",  rx_buffer[0]);
	pi_pad_set_function(PI_PAD_46_B7_SPIM0_SCK, PI_PAD_FUNC3);
}

void crop(uint8_t *img) {
    int ps = 0;
    for (int i =0; i < CAMERA_HEIGHT; i++) {
    	for (int j=0; j < CAMERA_WIDTH; j++) {
    		if (i < AT_INPUT_HEIGHT && j < AT_INPUT_WIDTH) {
    			img[ps] = img[i*CAMERA_WIDTH+j];
    			ps++;
    		}
    	}
    }
}

void equalize_histogram(uint8_t *img) {
    uint8_t pixel_val;
    uint32_t cumsum, level;
    for (int i=0; i<256; i++) {hist[i] = 0;}

    for (int i = 0; i < NUM_PIXELS; i++) {
        pixel_val = img[i];
        hist[pixel_val]++;
    }
    
    cumsum = 0;
    for (int i = 0; i < 256; i++) {
        cumsum += hist[i];
        level = (cumsum * 255) / NUM_PIXELS;
        levels[i] = (uint8_t) level;
    }
    
    for (int i = 0; i < NUM_PIXELS; i++) {
        pixel_val = img[i];
        img[i] = levels[pixel_val];
    }
}


static void cam_handler(void *arg) {
    pi_camera_control(&camera, PI_CAMERA_CMD_STOP, 0);
}

void capture_img_async() {
    pi_camera_control(&camera, PI_CAMERA_CMD_STOP, 0);
    pi_task_callback(&task, cam_handler, NULL);
    pi_camera_capture_async(&camera, Input_1, CAMERA_WIDTH * CAMERA_HEIGHT, &task);
    pi_camera_control(&camera, PI_CAMERA_CMD_START, 0);
    pi_task_wait_on(&task);
    crop(Input_1);
    /*equalize_histogram(Input_1);*/
}


void capture_img_sync() {
    pi_camera_control(&camera, PI_CAMERA_CMD_START, 0);
    pi_camera_capture(&camera, Input_1, (uint32_t) CAMERA_SIZE);
    pi_camera_control(&camera, PI_CAMERA_CMD_STOP, 0);
    crop(Input_1);
    /*equalize_histogram(Input_1);*/
}

void send_img() {
    for (int i = 0; i < AT_INPUT_HEIGHT; i++){
        pi_uart_write(&uart, Input_1 + (i * AT_INPUT_WIDTH), AT_INPUT_WIDTH);
    }
}

static int open_camera_himax(struct pi_device *device) {
    struct pi_himax_conf cam_conf;
    pi_himax_conf_init(&cam_conf);
    pi_open_from_conf(device, &cam_conf);
    if (pi_camera_open(device))
        return -1;
    pi_camera_control(&camera, PI_CAMERA_CMD_AEG_INIT, 0);
    rt_time_wait_us(1000000); //wait AEG init (takes ~100 ms)
    return 0;
}

static void RunNetwork() {
printf("Running on cluster\n");
#ifdef PERF
    printf("Start timer\n");
    gap_cl_starttimer();
    gap_cl_resethwtimer();
#endif
    AT_CNN((unsigned char *) Input_1, ResOut);
    printf("Runner completed\n");
}

int body(void){
	uint32_t voltage =1200;
    pi_freq_set(PI_FREQ_DOMAIN_FC, FREQ_FC*1000*1000);
    pi_freq_set(PI_FREQ_DOMAIN_CL, FREQ_CL*1000*1000);
	
	pi_hyperram_conf_init(&hyper_conf);
	pi_open_from_conf(&EXTERNAL_RAM, &hyper_conf);
	if (pi_ram_open(&EXTERNAL_RAM))
	{
		printf("Error ram open !\n");
		pmsis_exit(-3);
	}
    printf("hyperrram init complete\n");

    // open UART
    /*open_uart();   */
    open_spi();
    
    if (open_camera_himax(&camera)) {
        printf("Failed to open camera\n");
        pmsis_exit(-2);
    }

	// Open the cluster
	pi_cluster_conf_init(&conf);
	pi_open_from_conf(&cluster_dev, (void *)&conf);
	pi_cluster_open(&cluster_dev);

	// Task setup
	struct pi_cluster_task *task = pmsis_l2_malloc(sizeof(struct pi_cluster_task));
	if (task==NULL) {
	  printf("pi_cluster_task alloc Error!\n");
	  pmsis_exit(-1);
	}
	printf("Stack size is %d and %d\n",STACK_SIZE,SLAVE_STACK_SIZE );
	memset(task, 0, sizeof(struct pi_cluster_task));
	task->entry = &RunNetwork;
	task->stack_size = STACK_SIZE;
	task->slave_stack_size = SLAVE_STACK_SIZE;
	task->arg = NULL;

	// Allocate the output tensor
	ResOut = (NETWORK_OUT_TYPE *) AT_L2_ALLOC(0, NUM_FEATS*sizeof(NETWORK_OUT_TYPE));
	if (ResOut==0) {
		printf("Failed to allocate Memory for Result (%ld bytes)\n", 2*sizeof(char));
		return 1;
	}

	// Network Constructor
	// IMPORTANT: MUST BE CALLED AFTER THE CLUSTER IS ON!
	int err_const = AT_CONSTRUCT();
	if (err_const) {
	    printf("Graph constructor exited with error: %d\n", err_const);
	    return 1;
	}
	printf("Network Constructor was OK!\n");

    printf("entered main loop\n");
    while (1) {
        /*uart_read();*/
        
        start = rt_time_get_us();
        capture_img_async();
        printf("got img\n");
        
        for (int i = 0; i < 5; i++) {
            spi_read_status[0] = 0x00;
            send_spi(Input_1 + (i * 32));
            pi_time_wait_us(100);
        }
        printf("sent over spi\n");

        /*times[0] = rt_time_get_us() - start;*/
       
        /*start = rt_time_get_us();*/
        /*if (rx_buffer[0]) {*/
            /*send_img();*/
        /*} */
        /*times[1] = rt_time_get_us() - start;*/

        /*start = rt_time_get_us();*/
        /*if (rx_buffer[1] > 0) { //only do forward pass if we want > 0 channels*/
            /*pi_cluster_send_task_to_cl(&cluster_dev, task);*/
        /*}*/
        /*times[2] = rt_time_get_us() - start;*/
        
        /*start = rt_time_get_us();*/
        /*for (int i=0; i < rx_buffer[1]; i++) {*/
            /*pi_uart_write(&uart, ResOut + i*SPATIAL_DIM, SPATIAL_DIM); */
        /*}*/
        /*times[1] += rt_time_get_us() - start;*/

        /*pi_uart_write(&uart, times, 12); */
    }


	// Netwrok Destructor
	AT_DESTRUCT();
	pi_cluster_close(&cluster_dev);
	pmsis_exit(0);

	return 0;
}


int main(void)
{
    printf("\n\n\t *** ImageNet classification on GAP ***\n");
    return pmsis_kickoff((void *) body);
}

