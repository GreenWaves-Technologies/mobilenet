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
#include "bsp/bsp.h"
#include "bsp/buffer.h"
#include "bsp/camera/himax.h"
#include "bsp/ram.h"
#include "bsp/ram/hyperram.h"
#include "bsp/display/ili9341.h"

#include "main.h"


// Comment or Uncomment if using Himax camera or LCD on a board
//#define HAVE_CAMERA //uncomment if using himax camera
#ifdef HAVE_CAMERA 
	#define HAVE_LCD //uncomment if using LCD 
#endif
#ifndef HAVE_CAMERA
	#undef HAVE_LCD // HAVE_LCD can be set only if HAVE_CAMERA is defined
#endif

/* Defines */
#define NUM_CLASSES 	1001
#define AT_INPUT_SIZE 	(AT_INPUT_WIDTH*AT_INPUT_HEIGHT*AT_INPUT_COLORS)

#ifndef HAVE_CAMERA
	#define __XSTR(__s) __STR(__s)
	#define __STR(__s) #__s 
#else	
	#define CAMERA_WIDTH    (324)
	#define CAMERA_HEIGHT   (244)
	#define CAMERA_SIZE   	(CAMERA_HEIGHT*CAMERA_WIDTH)
#endif


#ifdef HAVE_LCD
	#define LCD_WIDTH    AT_INPUT_WIDTH
	#define LCD_HEIGHT   AT_INPUT_HEIGHT
#endif

typedef signed short int NETWORK_OUT_TYPE;

// Global Variables
struct pi_device camera;
static pi_buffer_t buffer;
struct pi_device HyperRam;

#ifdef HAVE_LCD
	struct pi_device display;	
#endif

L2_MEM NETWORK_OUT_TYPE *ResOut;
static uint32_t l3_buff;
AT_HYPERFLASH_FS_EXT_ADDR_TYPE AT_L3_ADDR = 0;


#ifdef HAVE_LCD

static int open_display(struct pi_device *device)
{
  struct pi_ili9341_conf ili_conf;

  pi_ili9341_conf_init(&ili_conf);
  pi_open_from_conf(device, &ili_conf);
  if (pi_display_open(device))
    return -1;
  if (pi_display_ioctl(device, PI_ILI_IOCTL_ORIENTATION, (void *)PI_ILI_ORIENTATION_90))
    return -1;

  return 0;
}
#endif


#ifdef HAVE_CAMERA

static int open_camera_himax(struct pi_device *device)
{
  struct pi_himax_conf cam_conf;

  pi_himax_conf_init(&cam_conf);
  pi_open_from_conf(device, &cam_conf);
  if (pi_camera_open(device))
    return -1;

  return 0;

}
#endif

static void RunNetwork()
{
  printf("Running on cluster\n");
#ifdef PERF
  printf("Start timer\n");
  gap_cl_starttimer();
  gap_cl_resethwtimer();
#endif
  AT_CNN(l3_buff, ResOut);
  printf("Runner completed\n");

}

int body(void)
{
	// Voltage-Frequency settings
	uint32_t voltage =1200;
	pi_freq_set(PI_FREQ_DOMAIN_FC, FREQ_FC);
	pi_freq_set(PI_FREQ_DOMAIN_CL, FREQ_CL);
	//PMU_set_voltage(voltage, 0);
	printf("Set VDD voltage as %.2f, FC Frequency as %d MHz, CL Frequency = %d MHz\n", 
		(float)voltage/1000, FREQ_FC/1000000, FREQ_CL/1000000);

	// Initialize the ram 
  	struct pi_hyperram_conf hyper_conf;
  	pi_hyperram_conf_init(&hyper_conf);
  	pi_open_from_conf(&HyperRam, &hyper_conf);
	if (pi_ram_open(&HyperRam))
	{
		printf("Error ram open !\n");
		pmsis_exit(-3);
	}

	// Allocate L3 buffer to store input data 
	if (pi_ram_alloc(&HyperRam, &l3_buff, (uint32_t) AT_INPUT_SIZE))
	{
		printf("Ram malloc failed !\n");
		pmsis_exit(-4);
	}

	// Open LCD
#ifdef HAVE_LCD
	if (open_display(&display))
	{
		printf("Failed to open display\n");
		pmsis_exit(-1);
	}
#endif


#ifdef HAVE_CAMERA
	// Allocate temp buffer for camera data
	uint8_t* Input_1 = (uint8_t*) pmsis_l2_malloc(CAMERA_SIZE*sizeof(char));
	if(!Input_1){
		printf("Failed allocation!\n");
		pmsis_exit(1);
	}

	// Open Camera 
	if (open_camera_himax(&camera))
	{
		printf("Failed to open camera\n");
		pmsis_exit(-2);
	}

	// Get an image 
    pi_camera_control(&camera, PI_CAMERA_CMD_START, 0);
    pi_camera_capture(&camera, Input_1, CAMERA_SIZE);
    pi_camera_control(&camera, PI_CAMERA_CMD_STOP, 0);

    // Image Cropping to [ AT_INPUT_HEIGHT x AT_INPUT_WIDTH ]
    int ps=0;
    for(int i =0;i<CAMERA_HEIGHT;i++){
    	for(int j=0;j<CAMERA_WIDTH;j++){
    		if (i<AT_INPUT_HEIGHT && j<AT_INPUT_WIDTH){
    			Input_1[ps] = Input_1[i*CAMERA_WIDTH+j];
    			ps++;        			
    		}
    	}
    } 	

#else
	// Allocate temp buffer for image data
	uint8_t* Input_1 = (uint8_t*) pmsis_l2_malloc(AT_INPUT_SIZE*sizeof(char));
	if(!Input_1){
		printf("Failed allocation!\n");
		pmsis_exit(1);
	}

	char *ImageName = __XSTR(AT_IMAGE);
	printf("Reading image from %s\n",ImageName);

	//Reading Image from Bridge
	img_io_out_t type = IMGIO_OUTPUT_CHAR;
	if (ReadImageFromFile(ImageName, AT_INPUT_WIDTH, AT_INPUT_HEIGHT, AT_INPUT_COLORS, Input_1, AT_INPUT_SIZE*sizeof(char), type, 0)) {
		printf("Failed to load image %s\n", ImageName);
		pmsis_exit(-1);
	}
	printf("Finished reading image %s\n", ImageName);
#endif

#ifdef HAVE_LCD
	// Config Buffer for LCD Display 
	buffer.data = Input_1;
	buffer.stride = 0;

	pi_buffer_init(&buffer, PI_BUFFER_TYPE_L2, Input_1);
	pi_buffer_set_stride(&buffer, 0);
	pi_buffer_set_format(&buffer, AT_INPUT_WIDTH, AT_INPUT_HEIGHT, 1, PI_BUFFER_FORMAT_GRAY);
	
	pi_display_write(&display, &buffer, 0, 0, AT_INPUT_WIDTH, AT_INPUT_HEIGHT);
#endif 

	//move input image to L3 Hyperram
#ifdef HAVE_CAMERA
	// Copy Single Channel Greyscale to 3 channel RGB: CH0-CH1-CH2 
	pi_ram_write(&HyperRam, (l3_buff), 									Input_1, (uint32_t) AT_INPUT_WIDTH*AT_INPUT_HEIGHT);
	pi_ram_write(&HyperRam, (l3_buff+AT_INPUT_WIDTH*AT_INPUT_HEIGHT), 	Input_1, (uint32_t) AT_INPUT_WIDTH*AT_INPUT_HEIGHT);
	pi_ram_write(&HyperRam, (l3_buff+2*AT_INPUT_WIDTH*AT_INPUT_HEIGHT), Input_1, (uint32_t) AT_INPUT_WIDTH*AT_INPUT_HEIGHT);
	pmsis_l2_malloc_free(Input_1, CAMERA_SIZE*sizeof(char));
#else
	// write greyscale image to RAM
	pi_ram_write(&HyperRam, (l3_buff), Input_1, (uint32_t) AT_INPUT_SIZE);
	pmsis_l2_malloc_free(Input_1, AT_INPUT_SIZE*sizeof(char));
#endif

	// Open the cluster
	struct pi_device cluster_dev;
	struct pi_cluster_conf conf;
	pi_cluster_conf_init(&conf);
	pi_open_from_conf(&cluster_dev, (void *)&conf);
	pi_cluster_open(&cluster_dev);

	// Task setup
	struct pi_cluster_task *task = pmsis_l2_malloc(sizeof(struct pi_cluster_task));
	if(task==NULL) {
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
	ResOut = (NETWORK_OUT_TYPE *) AT_L2_ALLOC(0, NUM_CLASSES*sizeof(NETWORK_OUT_TYPE));
	if (ResOut==0) {
		printf("Failed to allocate Memory for Result (%ld bytes)\n", 2*sizeof(char));
		return 1;
	}

	// Network Constructor
	// IMPORTANT: MUST BE CALLED AFTER THE CLUSTER IS ON!
	if (AT_CONSTRUCT())
	{
	  printf("Graph constructor exited with an error\n");
	  return 1;
	}
	printf("Network Constructor was OK!\n");

	// Dispatch task on the cluster 
	pi_cluster_send_task_to_cl(&cluster_dev, task);



	//Check Results
	int outclass, MaxPrediction = 0;
	for(int i=0; i<NUM_CLASSES; i++){
		if (ResOut[i] > MaxPrediction){
			outclass = i;
			MaxPrediction = ResOut[i];
		}
	}
	printf("Predicted class: %d\n", outclass);
	printf("With confidence: %d\n", MaxPrediction);


	// Performance counters
#ifdef PERF
	{
		unsigned int TotalCycles = 0, TotalOper = 0;
		printf("\n");
		for (int i=0; i<(sizeof(AT_GraphPerf)/sizeof(unsigned int)); i++) {
			printf("%45s: Cycles: %10d, Operations: %10d, Operations/Cycle: %f\n", AT_GraphNodeNames[i], AT_GraphPerf[i], AT_GraphOperInfosNames[i], ((float) AT_GraphOperInfosNames[i])/ AT_GraphPerf[i]);
			TotalCycles += AT_GraphPerf[i]; TotalOper += AT_GraphOperInfosNames[i];
		}
		printf("\n");
		printf("\t\t\t %s: Cycles: %10d, Operations: %10d, Operations/Cycle: %f\n", "Total", TotalCycles, TotalOper, ((float) TotalOper)/ TotalCycles);
		printf("\n");
	}
#endif

	// Netwrok Destructor
	AT_DESTRUCT();

	pmsis_exit(0);

	return 0;
}


int main(void)
{
    printf("\n\n\t *** Image classification models on GAP ***\n\n");
    return pmsis_kickoff((void *) body);
}

