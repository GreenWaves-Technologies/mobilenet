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
#ifdef HAVE_CAMERA
#include "bsp/camera/himax.h"
#endif

#include "main.h"

/* Defines */
#define NUM_CLASSES 	1001
#define AT_INPUT_SIZE 	(AT_INPUT_WIDTH*AT_INPUT_HEIGHT*AT_INPUT_COLORS)

#define __XSTR(__s) __STR(__s)
#define __STR(__s) #__s 
#ifdef HAVE_CAMERA	
	#define CAMERA_WIDTH    (324)
	#define CAMERA_HEIGHT   (244)
	#define CAMERA_SIZE   	(CAMERA_HEIGHT*CAMERA_WIDTH)
	struct pi_device camera;
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

typedef signed short int NETWORK_OUT_TYPE;
// Global Variables
L2_MEM NETWORK_OUT_TYPE *ResOut;
AT_HYPERFLASH_FS_EXT_ADDR_TYPE AT_L3_ADDR = 0;

static void RunNetwork()
{
  printf("Running on cluster\n");
#ifdef PERF
  printf("Start timer\n");
  gap_cl_starttimer();
  gap_cl_resethwtimer();
#endif
  int start_timer = gap_cl_readhwtimer();
  AT_CNN(ResOut);
  int finish_timer = gap_cl_readhwtimer() - start_timer;
  printf("Runner completed: %d Cycles\n", finish_timer);

}

int body(void)
{
	// Voltage-Frequency settings
	uint32_t voltage =1200;
	pi_freq_set(PI_FREQ_DOMAIN_FC, FREQ_FC*1000*1000);
	pi_freq_set(PI_FREQ_DOMAIN_CL, FREQ_CL*1000*1000);
	pi_freq_set(PI_FREQ_DOMAIN_PERIPH, FREQ_FC*1000*1000);
	//PMU_set_voltage(voltage, 0);
	printf("Set VDD voltage as %.2f, FC Frequency as %d MHz, CL Frequency = %d MHz, PERIIPH Frequency = %d\n", 
		(float)voltage/1000, pi_freq_get(PI_FREQ_DOMAIN_FC), pi_freq_get(PI_FREQ_DOMAIN_CL), pi_freq_get(PI_FREQ_DOMAIN_PERIPH));

	// Open the cluster
	struct pi_device cluster_dev;
	struct pi_cluster_conf conf;
	pi_cluster_conf_init(&conf);
	pi_open_from_conf(&cluster_dev, (void *)&conf);
	pi_cluster_open(&cluster_dev);

	// Allocate the output tensor
	ResOut = (NETWORK_OUT_TYPE *) AT_L2_ALLOC(0, NUM_CLASSES*sizeof(NETWORK_OUT_TYPE));
	if (ResOut==0) {
		printf("Failed to allocate Memory for Result (%ld bytes)\n", 2*sizeof(char));
	  	pmsis_exit(-1);
	}

	// Network Constructor
	// IMPORTANT: MUST BE CALLED AFTER THE CLUSTER IS ON!
	int err_const = AT_CONSTRUCT();
	if (err_const)
	{
	  printf("Graph constructor exited with error: %d\n", err_const);
	  pmsis_exit(-2);
	}
	printf("Network Constructor was OK!\n");

#ifdef HAVE_CAMERA
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

	#ifdef MODEL_HWC // HWC does not have the image formatter in front
		for (int i=0; i<AT_INPUT_SIZE; i++) Input_1[i] -= 128;
	#endif

	// Task setup
	struct pi_cluster_task task;
	printf("Stack size is %d and %d\n",STACK_SIZE,SLAVE_STACK_SIZE );
	task.entry = &RunNetwork;
	task.stack_size = STACK_SIZE;
	task.slave_stack_size = SLAVE_STACK_SIZE;
	task.arg = NULL;
	// Dispatch task on the cluster 
	pi_cluster_send_task_to_cl(&cluster_dev, &task);

	//Check Results
	int outclass = 0, MaxPrediction = 0;
	for(int i=0; i<NUM_CLASSES; i++){
		if (ResOut[i] > MaxPrediction){
			outclass = i;
			MaxPrediction = ResOut[i];
		}
	}
	printf("Model:\t%s\n\n", __XSTR(AT_MODEL_PREFIX));
	printf("Predicted class:\t%d\n", outclass);
	printf("With confidence:\t%d\n", MaxPrediction);


	// Performance counters
#ifdef PERF
	{
		unsigned int TotalCycles = 0, TotalOper = 0;
		printf("\n");
		for (unsigned int i=0; i<(sizeof(AT_GraphPerf)/sizeof(unsigned int)); i++) {
			printf("%45s: Cycles: %10d, Operations: %10d, Operations/Cycle: %f\n", AT_GraphNodeNames[i], AT_GraphPerf[i], AT_GraphOperInfosNames[i], ((float) AT_GraphOperInfosNames[i])/ AT_GraphPerf[i]);
			TotalCycles += AT_GraphPerf[i]; TotalOper += AT_GraphOperInfosNames[i];
		}
		printf("\n");
		printf("%45s: Cycles: %10d, Operations: %10d, Operations/Cycle: %f\n", "Total", TotalCycles, TotalOper, ((float) TotalOper)/ TotalCycles);
		printf("\n");
	}
#endif

	// Netwrok Destructor
	AT_DESTRUCT();
	AT_L2_FREE(0, ResOut, NUM_CLASSES*sizeof(NETWORK_OUT_TYPE));
	pi_cluster_close(&cluster_dev);
	if(strcmp(__XSTR(AT_MODEL_PREFIX),"mobilenet_v1_1_0_224_quant")==0){
		if(outclass==42 && MaxPrediction==9561){
				printf("Test successful!\n");
				pmsis_exit(0);
			}
		else{
				printf("Wrong results!\n");
				pmsis_exit(-1);
			}
	}

	pmsis_exit(0);

	return 0;
}


int main(void)
{
    printf("\n\n\t *** ImageNet classification on GAP ***\n");
    return pmsis_kickoff((void *) body);
}

