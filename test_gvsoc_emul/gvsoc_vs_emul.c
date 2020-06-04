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

#include <stdio.h>
#include <limits.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

#include "main.h"

#ifndef __EMUL__
	#define __XSTR(__s) __STR(__s)
	#define __STR(__s) #__s 
#endif
#define AT_INPUT_SIZE 	(AT_INPUT_WIDTH*AT_INPUT_HEIGHT*AT_INPUT_COLORS)
#define NUM_CLASSES 1001

#if MODEL_ID==16
	typedef signed char NETWORK_OUT_TYPE;
#else
	typedef signed short int NETWORK_OUT_TYPE;
#endif
L2_MEM NETWORK_OUT_TYPE *ResOut;
unsigned char *Input_1;
char *ImageName = NULL;

AT_HYPERFLASH_FS_EXT_ADDR_TYPE AT_L3_ADDR = 0;

static void RunNetwork()
{
  printf("Running on cluster\n");
  AT_CNN(Input_1, ResOut);
  printf("Runner completed\n");
  printf("\n");

}

int body(void)
{
/*-------------------reading input data-----------------------------*/
	Input_1 = (unsigned char *) AT_L2_ALLOC(0, AT_INPUT_SIZE*sizeof(char));
	if (Input_1==0){
		printf("Failed to allocate Memory for Input (%ld bytes)\n", AT_INPUT_SIZE*sizeof(char));
		return 1;		
	}

	#ifndef __EMUL__
		ImageName = __XSTR(AT_IMAGE);
	#endif
	printf("Reading image from %s\n",ImageName);
	//Reading Image from Bridge
	img_io_out_t type = IMGIO_OUTPUT_CHAR;
	
	if (ReadImageFromFile(ImageName, AT_INPUT_WIDTH, AT_INPUT_HEIGHT, AT_INPUT_COLORS, Input_1, AT_INPUT_SIZE*sizeof(char), type, 0)) {
		printf("Failed to load image %s\n", ImageName);
		#ifndef __EMUL__
			pmsis_exit(0);
		#else
			return 0;
		#endif
	}
	printf("Finished reading image %s\n", ImageName);

#ifndef __EMUL__
/*-------------------OPEN THE CLUSTER-------------------------------*/
	struct pi_device cluster_dev;
	struct pi_cluster_conf conf;
	pi_cluster_conf_init(&conf);
	pi_open_from_conf(&cluster_dev, (void *)&conf);
	pi_cluster_open(&cluster_dev);
/*--------------------------TASK SETUP------------------------------*/
	struct pi_cluster_task *task = pmsis_l2_malloc(sizeof(struct pi_cluster_task));
	if(task==NULL) {
		printf("pi_cluster_task alloc Error!\n");
		#ifndef __EMUL__
			pmsis_exit(0);
		#else
			return 0;
		#endif
	}
	printf("Stack size is %d and %d\n",STACK_SIZE,SLAVE_STACK_SIZE );
	memset(task, 0, sizeof(struct pi_cluster_task));
	task->entry = &RunNetwork;
	task->stack_size = STACK_SIZE;
	task->slave_stack_size = SLAVE_STACK_SIZE;
	task->arg = NULL;
#endif

/*--------------------CONSTRUCT THE NETWORK-------------------------*/
	/*--------------ALLOCATE THE OUTPUT TENSOR---------*/
	ResOut = (NETWORK_OUT_TYPE *) AT_L2_ALLOC(0, NUM_CLASSES*sizeof(NETWORK_OUT_TYPE));
	if (ResOut==0) {
		printf("Failed to allocate Memory for Result (%ld bytes)\n", NUM_CLASSES*sizeof(NETWORK_OUT_TYPE));
		return 1;
	}

    printf("Constructor\n");
	// IMPORTANT - MUST BE CALLED AFTER THE CLUSTER IS SWITCHED ON!!!!
	if (AT_CONSTRUCT())
	{
	  printf("Graph constructor exited with an error\n");
	  return 1;
	}
	printf("Constructor was OK!\n");

/*-----------------------CALL THE MAIN FUNCTION----------------------*/
//	printf("Call cluster\n");
#ifndef __EMUL__
	pi_cluster_send_task_to_cl(&cluster_dev, task);
#else
	RunNetwork(NULL);
#endif

/*-----------------------CALL THE MAIN FUNCTION----------------------*/
  //Checki Results
  printf("OUTPUT:\t");
  int outclass, MaxPrediction = 0;
  for(int i=0; i<NUM_CLASSES; i++){
    if (ResOut[i] > MaxPrediction){
      outclass = i;
      MaxPrediction = ResOut[i];
    }
    printf("%d, ", ResOut[i]);
  }
  printf("\n");
  printf("Predicted class: %d\n", outclass);
  printf("With confidence: %d\n", MaxPrediction);

/*-----------------------Desctruct the AT model----------------------*/
	AT_DESTRUCT();
#ifndef __EMUL__
	pmsis_exit(0);
#endif
	printf("Ended\n");
	return 0;
}

#ifndef __EMUL__
int main(void)
{
    printf("\n\n\t *** IMAGENET GVSOC ***\n\n");
    return pmsis_kickoff((void *) body);
}
#else
int main(int argc, char *argv[])
{
    if (argc < 2)
    {
        printf("Usage: mnist [image_file]\n");
        exit(-1);
    }
    ImageName = argv[1];
    printf("\n\n\t *** IMAGENET EMUL ***\n\n");
    body();
    return 0;
}
#endif
