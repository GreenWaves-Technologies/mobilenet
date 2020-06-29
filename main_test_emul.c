/*
 * Copyright (C) 2017 GreenWaves Technologies
 * All rights reserved.
 *
 * This software may be modified and distributed under the terms
 * of the BSD license.  See the LICENSE file for details.
 *
 */
#define _FILE_OFFSET_BITS 64

#include <stdio.h>

#include "main.h"

#include "ordered_synset.h"
#include <dirent.h>

#define __XSTR(__s) __STR(__s)
#define __STR(__s) #__s


#ifdef PERF
#undef PERF
#endif

#define AT_INPUT_SIZE (AT_INPUT_WIDTH*AT_INPUT_HEIGHT*AT_INPUT_COLORS)

#ifndef STACK_SIZE
#define STACK_SIZE     2048 
#endif

#define MAXCHAR 1000
#define NUM_CLASSES 1001

AT_HYPERFLASH_FS_EXT_ADDR_TYPE AT_L3_ADDR;

// Softmax always outputs Q15 short int even from 8 bit input
#if MODEL_ID==16 // mobilenetv2
signed char ResOut[NUM_CLASSES];
#else
short int ResOut[NUM_CLASSES];
#endif
//
unsigned char ImgIn[AT_INPUT_SIZE];


int main(int argc, char *argv[]) 
{
  if (argc < 2) {
    printf("Usage: %s [dataset_folder]\n", argv[0]);
    exit(1);
  }

  char *ImageName = argv[1];

  printf("Entering main controller\n");
  printf("Constructor\n");

  if (ReadImageFromFile(ImageName, AT_INPUT_WIDTH, AT_INPUT_HEIGHT, AT_INPUT_COLORS, ImgIn, AT_INPUT_SIZE*sizeof(unsigned char), IMGIO_OUTPUT_CHAR, 0)){
  	return 1;
  }

  // IMPORTANT - MUST BE CALLED AFTER THE CLUSTER IS SWITCHED ON!!!!
  if (AT_CONSTRUCT())
  {
    printf("Graph constructor exited with an error\n");
    return 1;
  }

  AT_CNN(ImgIn, ResOut);

  AT_DESTRUCT();

  printf("Ended\n");
  return 0;
}

