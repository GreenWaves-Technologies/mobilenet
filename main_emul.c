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

//#include "mobilenet_v1_0_25_128_quant.h"
#include "mobilenet_v1_1_0_224_quant.h"
//#include "mobilenet_v2_1_0_224_quant.h"
//#include "mobilenet_v3_large_1_0_224_quant.h"

#include "ordered_synset.h"
#include "ImgIO.h"

#include <string.h>
#include <dirent.h>
#include <sys/types.h>

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

AT_HYPERFLASH_FS_EXT_ADDR_TYPE __PREFIX(_L3_Flash);


// Softmax always outputs Q15 short int even from 8 bit input
//short int ResOut[NUM_CLASSES];
signed char ResOut[NUM_CLASSES];
unsigned char ImgIn[AT_INPUT_SIZE];
unsigned int TOTAL_COUNTER, CURRENT_COUNTER;

struct dirent64
  {
    __ino64_t d_ino;
    __off64_t d_off;
    unsigned short int d_reclen;
    unsigned char d_type;
    char d_name[256];   /* We must not include limits.h! */
  };

static int RunNetwork()
{
  printf("I am here\n");
  __PREFIX(CNN)(ImgIn, ResOut);
  //Checki Results
  int outclass, MaxPrediction = 0;
  for(int i=0; i<NUM_CLASSES; i++){
    if (ResOut[i] > MaxPrediction){
      outclass = i;
      MaxPrediction = ResOut[i];
    }
  }
  return outclass;
}

int read_folder(char *dir, int label)
{
  struct dirent64 *dp;
  DIR *dfd;
  int predicted = 0;
  int counter = 0;
  int result;
  char filename_qfd[1000];

  /*--------------------iterate over files in dir------------------------*/
  if ((dfd = opendir(dir)) == NULL)
  {
    fprintf(stderr, "Can't open %s\n", dir);
    return 0;
  }
  while ((dp = readdir64(dfd)) != NULL)
  {
    struct stat stbuf ;
    sprintf(filename_qfd, "%s/%s", dir, dp->d_name);
    if( stat(filename_qfd, &stbuf) == -1 ){
    printf("%s \n", strerror(errno));

      printf("Unable to stat file: %s\n",filename_qfd) ;
      continue;
    }

    if ( ( stbuf.st_mode & S_IFMT ) == S_IFDIR ){
      continue;
     // Skip directories
    } else {
      //Reading Image from Bridge
      if (ReadImageFromFile(filename_qfd, AT_INPUT_WIDTH, AT_INPUT_HEIGHT, AT_INPUT_COLORS, ImgIn, AT_INPUT_SIZE*sizeof(unsigned char), IMGIO_OUTPUT_CHAR, 0)) {
        continue;
      }
      counter++;
      printf("Going to run convolution on %s\n", filename_qfd);
      /*------------------Execute the function "RunNetwork"--------------*/
      result = RunNetwork(NULL);
      printf("Inference run OK\n");

      //printf("label - %d\tpredicted - %d\n", label, result);
      predicted += (result==label);
    }
  }
  printf("class %d: %d/%d\n", label, predicted, counter);
  if (!counter) printf("%s\n", dir);
  TOTAL_COUNTER += counter;
  CURRENT_COUNTER = counter;
  return predicted;
}

int main(int argc, char *argv[]) 
{
  if (argc < 2) {
    printf("Usage: %s [dataset_folder]\n", argv[0]);
    exit(1);
  }

  struct dirent *dp;
  DIR *dfd;
  char *dir = argv[1];

  printf("Entering main controller\n");
  printf("Constructor\n");

  // IMPORTANT - MUST BE CALLED AFTER THE CLUSTER IS SWITCHED ON!!!!
  if (__PREFIX(CNN_Construct)())
  {
    printf("Graph constructor exited with an error\n");
    return 1;
  }
  int TOTAL_PREDICTED = 0;
  float avg_perc = 0;
  float class_perc;
  int class_predicted;
  char *class_dir[100];
  for (int i=0; i<NUM_CLASSES; i++)
  {
      printf("%s:\t", ORDERED_SYNSET[i]);
      sprintf(class_dir , "%s/%s" , dir, ORDERED_SYNSET[i]);
      class_predicted = read_folder(class_dir, i);
      TOTAL_PREDICTED += class_predicted;
      if (CURRENT_COUNTER == 0)
        class_perc = 0;
      else
        class_perc = (float) class_predicted / (float) CURRENT_COUNTER;
      avg_perc += class_perc;
  }


  printf("well predicted: %d/%d = %f\n", TOTAL_PREDICTED, TOTAL_COUNTER, (float)TOTAL_PREDICTED/TOTAL_COUNTER );
  printf("Avergae Precision: %f\n", avg_perc / NUM_CLASSES);

  __PREFIX(CNN_Destruct)();

  printf("Ended\n");
  return 0;
}

