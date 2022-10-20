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
#include "main.h"

/* Defines */
#define NUM_CLASSES 	1001
#define AT_INPUT_SIZE 	(AT_INPUT_WIDTH*AT_INPUT_HEIGHT*AT_INPUT_COLORS)

#define __XSTR(__s) __STR(__s)
#define __STR(__s) #__s 

typedef signed short int NETWORK_OUT_TYPE;
// Global Variables
L2_MEM NETWORK_OUT_TYPE *ResOut;
AT_HYPERFLASH_FS_EXT_ADDR_TYPE AT_L3_ADDR = 0;
AT_HYPERFLASH_FS_EXT_ADDR_TYPE AT_L3_2_ADDR = 0;

static void RunNetwork()
{
  printf("Running on cluster\n");
#ifdef PERF
  printf("Start timer\n");
  gap_cl_starttimer();
  gap_cl_resethwtimer();
#endif

  GPIO_HIGH();
  AT_CNN(ResOut);
  GPIO_LOW();
}

int body(void)
{
  OPEN_GPIO_MEAS();

	// Open the cluster
	struct pi_device cluster_dev;
	struct pi_cluster_conf conf;
	pi_cluster_conf_init(&conf);
	conf.cc_stack_size = STACK_SIZE;
                     // Enable the special icache for the master core
  conf.icache_conf = PI_CLUSTER_MASTER_CORE_ICACHE_ENABLE |
		                 // Enable the prefetch for all the cores, it's a 9bits mask (from bit 2 to bit 10), each bit correspond to 1 core
		                 PI_CLUSTER_ICACHE_PREFETCH_ENABLE |
		                 // Enable the icache for all the cores
		                 PI_CLUSTER_ICACHE_ENABLE;
	pi_open_from_conf(&cluster_dev, (void *)&conf);
	pi_cluster_open(&cluster_dev);

	// Voltage-Frequency settings
	pi_freq_set(PI_FREQ_DOMAIN_FC, FREQ_FC*1000*1000);
	pi_freq_set(PI_FREQ_DOMAIN_CL, FREQ_CL*1000*1000);
	pi_freq_set(PI_FREQ_DOMAIN_PERIPH, FREQ_PE*1000*1000);
	printf("Set FC Frequency = %d MHz, CL Frequency = %d MHz, PERIIPH Frequency = %d MHz\n",
			pi_freq_get(PI_FREQ_DOMAIN_FC), pi_freq_get(PI_FREQ_DOMAIN_CL), pi_freq_get(PI_FREQ_DOMAIN_PERIPH));
	#ifdef VOLTAGE
	pi_pmu_voltage_set(PI_PMU_VOLTAGE_DOMAIN_CHIP, VOLTAGE);
	pi_pmu_voltage_set(PI_PMU_VOLTAGE_DOMAIN_CHIP, VOLTAGE);
	#endif
	printf("Voltage: %dmV\n", pi_pmu_voltage_get(PI_PMU_VOLTAGE_DOMAIN_CHIP));

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

#ifndef FAKE_INPUT
	char *ImageName = __XSTR(AT_IMAGE);
	//Reading Image from Bridge
	img_io_out_t type = IMGIO_OUTPUT_CHAR;
	if (ReadImageFromFile(ImageName, AT_INPUT_WIDTH, AT_INPUT_HEIGHT, AT_INPUT_COLORS, Input_1, AT_INPUT_SIZE*sizeof(char), type, 0)) {
		printf("Failed to load image %s\n", ImageName);
		pmsis_exit(-1);
	}
	printf("Finished reading image\n");
#endif // FAKE_INPUT
	#ifdef MODEL_HWC // HWC does not have the image formatter in front
		for (int i=0; i<AT_INPUT_SIZE; i++) Input_1[i] -= 128;
	#endif

	// Task setup
	struct pi_cluster_task* task = (struct pi_cluster_task*)pi_l2_malloc(sizeof(struct pi_cluster_task));

	printf("Stack size is %d and %d\n",STACK_SIZE,SLAVE_STACK_SIZE );
	printf("Model:\t%s\n\n", __XSTR(AT_MODEL_PREFIX));
    pi_cluster_task(task, (void (*)(void *))&RunNetwork, NULL);
    pi_cluster_task_stacks(task, NULL, SLAVE_STACK_SIZE);
	// Dispatch task on the cluster 
	pi_cluster_send_task_to_cl(&cluster_dev, task);

	//Check Results
	int outclass = 0, MaxPrediction = 0;
	for(int i=0; i<NUM_CLASSES; i++){
		if (ResOut[i] > MaxPrediction){
			outclass = i;
			MaxPrediction = ResOut[i];
		}
	}
	printf("Predicted class:\t%d\n", outclass);
	printf("With confidence:\t%d\n", MaxPrediction);


	// Performance counters
#ifdef PERF
    {
      unsigned int TotalCycles = 0, TotalOper = 0;
      printf("\n");
      for (unsigned int i=0; i<(sizeof(AT_GraphPerf)/sizeof(unsigned int)); i++) {
        TotalCycles += AT_GraphPerf[i]; TotalOper += AT_GraphOperInfosNames[i];
      }
      for (unsigned int i=0; i<(sizeof(AT_GraphPerf)/sizeof(unsigned int)); i++) {
        printf("%45s: Cycles: %12u, Cyc%%: %5.1f%%, Operations: %12u, Op%%: %5.1f%%, Operations/Cycle: %f\n", AT_GraphNodeNames[i], AT_GraphPerf[i], 100*((float) (AT_GraphPerf[i]) / TotalCycles), AT_GraphOperInfosNames[i], 100*((float) (AT_GraphOperInfosNames[i]) / TotalOper), ((float) AT_GraphOperInfosNames[i])/ AT_GraphPerf[i]);
      }
      printf("\n");
      printf("%45s: Cycles: %12u, Cyc%%: 100.0%%, Operations: %12u, Op%%: 100.0%%, Operations/Cycle: %f\n", "Total", TotalCycles, TotalOper, ((float) TotalOper)/ TotalCycles);
      printf("\n");
    }
#endif

	// Netwrok Destructor
	AT_DESTRUCT();
	AT_L2_FREE(0, ResOut, NUM_CLASSES*sizeof(NETWORK_OUT_TYPE));
	pi_cluster_close(&cluster_dev);
	if((strcmp(__XSTR(AT_MODEL_PREFIX),"mobilenet_v1_1_0_224_quant")==0) || (strcmp(__XSTR(AT_MODEL_PREFIX),"mobilenet_v2_1_0_224_quant")==0)){
		if(outclass==42){
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

