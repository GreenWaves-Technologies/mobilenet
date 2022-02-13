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
/*#include "spi-wifi/spi_wifi.c"*/
#include "spi-wifi/spi_wifi.h"
#include "cam/cam.h"
#include "main.h"

/*#define BAUD 3000000*/
/*#define __XSTR(__s) __STR(__s)*/
/*#define __STR(__s) #__s*/
#define HIDDEN_WIDTH 28
#define HIDDEN_HEIGHT 28
#define HIDDEN_CHANNEL 32
#define SPATIAL_DIM (HIDDEN_WIDTH * HIDDEN_HEIGHT)
#define NUM_FEATS 	(HIDDEN_CHANNEL * SPATIAL_DIM)
/*#define AT_INPUT_SIZE 	(AT_INPUT_WIDTH*AT_INPUT_HEIGHT*AT_INPUT_COLORS)*/
/*#define NUM_PIXELS (AT_INPUT_WIDTH*AT_INPUT_HEIGHT)*/
/*#define CAMERA_WIDTH    (324)*/
/*#define CAMERA_HEIGHT   (244)*/
/*#define CAMERA_SIZE   	(CAMERA_HEIGHT*CAMERA_WIDTH)*/
#define EXTERNAL_RAM HyperRam
typedef signed char NETWORK_OUT_TYPE;

AT_HYPERFLASH_FS_EXT_ADDR_TYPE AT_L3_ADDR = 0;
L2_MEM NETWORK_OUT_TYPE *ResOut;
RT_L2_DATA uint32_t times[3];
RT_L2_DATA uint8_t Input_1[CAMERA_WIDTH*CAMERA_HEIGHT];
RT_L2_DATA uint8_t levels[256];
static pi_buffer_t buffer;
/*static pi_task_t task;*/
static uint8_t *rx_buffer;
struct pi_device camera;
struct pi_device uart;
struct pi_uart_conf uart_conf;
uint32_t start;
struct pi_device HyperRam;
struct pi_hyperram_conf hyper_conf;
struct pi_device cluster_dev;
struct pi_cluster_conf conf;


/*void open_uart() {*/
    /*pi_uart_conf_init(&uart_conf);*/
    /*uart_conf.baudrate_bps = BAUD;*/
    /*uart_conf.uart_id = 0;*/
    /*uart_conf.enable_tx = 1;*/
    /*uart_conf.enable_rx = 1;*/
    /*pi_open_from_conf(&uart, &uart_conf);*/
    /*if (pi_uart_open(&uart)) {*/
        /*printf("uart open failed\n");*/
    /*} else {*/
        /*printf("uart open\n");*/
    /*}*/
/*}*/


/*void uart_read() {*/
	/*pi_pad_set_function(PI_PAD_46_B7_SPIM0_SCK, PI_PAD_FUNC0);*/
    /*rx_buffer = (uint8_t *) pmsis_l2_malloc((uint32_t) 2);*/
    /*pi_task_t wait_task = {0};*/
    /*pi_task_block(&wait_task);*/
    /*pi_uart_read_async(&uart, rx_buffer, 2, &wait_task);*/
    /*pi_task_wait_on(&wait_task);*/
    /*printf("waiting over, got 1 byte with value %d\n",  rx_buffer[0]);*/
	/*pi_pad_set_function(PI_PAD_46_B7_SPIM0_SCK, PI_PAD_FUNC3);*/
/*}*/



/*void send_img() {*/
    /*for (int i = 0; i < AT_INPUT_HEIGHT; i++){*/
        /*pi_uart_write(&uart, Input_1 + (i * AT_INPUT_WIDTH), AT_INPUT_WIDTH);*/
    /*}*/
/*}*/

static void RunNetwork() {
    AT_CNN((unsigned char *) Input_1, ResOut);
}

int body(void){
	uint32_t voltage =1200;
    pi_freq_set(PI_FREQ_DOMAIN_FC, FREQ_FC*1000*1000);
    pi_freq_set(PI_FREQ_DOMAIN_CL, FREQ_CL*1000*1000);
	
	pi_hyperram_conf_init(&hyper_conf);
	pi_open_from_conf(&EXTERNAL_RAM, &hyper_conf);
	if (pi_ram_open(&EXTERNAL_RAM)) {
		printf("Error ram open !\n");
		pmsis_exit(-3);
	}
    printf("hyperrram init complete\n");

    // open SPI
    if(initializeSPI()) {
        printf("Failed to open SPI\n");
        pmsis_exit(-1);
    }
    printf("SPI init complete\n");

    
    if (openCamera()) {
        printf("Failed to open camera\n");
        pmsis_exit(-2);
    }
    printf("camera init complete\n");

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
    printf("cluster init complete\n");
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
    /*while (1) {*/
    /*for(int i = 0; i < 100 ;i++) {*/
    while (1) {
        /*uart_read();*/
        /*start = rt_time_get_us();*/
        captureImgAsync(Input_1);
        /*printf("got img\n");*/
        
        /*for (int i = 0; i < 5; i++) {*/
            /*spi_read_status[0] = 0x00;*/
            /*send_spi(Input_1 + (i * 32));*/
            /*pi_time_wait_us(100);*/
        /*}*/
        /*printf("sent over spi\n");*/

        /*times[0] = rt_time_get_us() - start;*/
       
        /*start = rt_time_get_us();*/
        /*if (rx_buffer[0]) {*/
            /*send_img();*/
        /*} */
        /*times[1] = rt_time_get_us() - start;*/

        /*start = rt_time_get_us();*/
        pi_cluster_send_task_to_cl(&cluster_dev, task);
        printf("forward pass done");
        /*times[2] = rt_time_get_us() - start;*/
        
        transmitSPI(Input_1, AT_INPUT_SIZE, 0);
        transmitSPI(ResOut, 8*SPATIAL_DIM, 0);
        /*start = rt_time_get_us();*/
        /*for (int i=0; i < 8; i++) {*/
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

