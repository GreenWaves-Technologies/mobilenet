/*
 * Copyright (C) 2017 GreenWaves Technologies
 * All rights reserved.
 *
 * This software may be modified and distributed under the terms
 * of the BSD license.  See the LICENSE file for details.
 *
 */

#include <stdio.h>

//#include "mobilenet_v1_0_25_128_quant.h"
#include "mobilenet_v2_1_0_224_quant.h"
//#include "mobilenet_v3_large_1_0_224_quant.h"

#include "ordered_synset.h"
#include "ImgIO.h"

#include <string.h>
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

AT_HYPERFLASH_FS_EXT_ADDR_TYPE __PREFIX(_L3_Flash);


// Softmax always outputs Q15 short int even from 8 bit input
L2_MEM short int *ResOut;
L2_MEM unsigned char imgin_unsigned[AT_INPUT_SIZE];
L2_MEM signed char *imgin_signed = imgin_unsigned;

static int get_label_from_dirname(char *dir_name){
  char *temp;
  temp = strrchr(dir_name, '/') + 1;
  if (temp==NULL){
    return 0;
  }
  for (int i=0; i<NUM_CLASSES; i++){
    if (!(strcmp(ORDERED_SYNSET[i], temp))){
      printf("%s == %s\n", ORDERED_SYNSET[i], temp);
      return i;
    }
  }
  return 0;
}

static int RunNetwork()
{
  __PREFIX(CNN)(imgin_signed, ResOut);
  //Checki Results
  int outclass, MaxPrediction = 0;
  for(int i=0; i<NUM_CLASSES; i++){
    if (ResOut[i] > MaxPrediction){
      outclass = i;
    }
  }
  return outclass;
}

int read_folder(char *dir)
{
  printf("%s\n", dir);
  struct dirent *dp;
  DIR *dfd;
  int predicted = 0;
  int result, label;
  char filename_qfd[100];

  /*--------------------iterate over files in dir------------------------*/
  if ((dfd = opendir(dir)) == NULL)
  {
    fprintf(stderr, "Can't open %s\n", dir);
    return 0;
  }
  while ((dp = readdir(dfd)) != NULL){
    struct stat stbuf ;
    sprintf( filename_qfd , "%s/%s" ,dir,dp->d_name);
    if( stat(filename_qfd, &stbuf) == -1 ){
      printf("Unable to stat file: %s\n",filename_qfd) ;
      continue;
    }

    if (!(strcmp(dp->d_name, "."))) continue;
    if (!(strcmp(dp->d_name, ".."))) continue;

    if ( ( stbuf.st_mode & S_IFMT ) == S_IFDIR ){
      predicted += read_folder(filename_qfd);
     // Skip directories
    } else {
      label = get_label_from_dirname(dir);
      printf("label = %d\n", label);
      //Reading Image from Bridge
      if (ReadImageFromFile(filename_qfd, AT_INPUT_WIDTH, AT_INPUT_HEIGHT, AT_INPUT_COLORS, imgin_unsigned, AT_INPUT_SIZE*sizeof(unsigned char), 0, 0)) {
        printf("Failed to load image %s\n", filename_qfd);
        return 1;
      }
      /*--------------------convert to signed in [-128:127]----------------*/
      for(int i=0; i<AT_INPUT_SIZE; i++){
        imgin_signed[i] = (signed char) ( ((int) (imgin_unsigned[i])) - 128);
      }
      #ifdef PRINT_IMAGE
        for (int i=0; i<AT_INPUT_SIZE; i++) {
            printf("%03d, ", __PREFIX(_L2_Memory[i]));
          }
          printf("\n");
      #endif
      /*----------------------Allocate output-----------------------------*/
      ResOut = (short int *) AT_L2_ALLOC(0, NUM_CLASSES*sizeof(short int));
      if (ResOut==0) {
        printf("Failed to allocate Memory for Result (%ld bytes)\n", NUM_CLASSES*sizeof(short int));
        return 1;
      }

      /*------------------Execute the function "RunNetwork"--------------*/
      result = RunNetwork(NULL);
      if (result==label){
        predicted++;
      } 
    }
    return predicted;
  }
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
  read_folder(dir);
  
  __PREFIX(CNN_Destruct)();

  printf("Ended\n");
  return 0;
}

