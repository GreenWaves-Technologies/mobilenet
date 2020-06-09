# Copyright (C) 2017 GreenWaves Technologies
# All rights reserved.

# This software may be modified and distributed under the terms
# of the BSD license.  See the LICENSE file for details.

ifndef GAP_SDK_HOME
  $(error Source sourceme in gap_sdk first)
endif

include common.mk

ifeq ($(AT_INPUT_WIDTH), 224)
	IMAGE=$(CURDIR)/images/ILSVRC2012_val_00011158_224.ppm
endif
ifeq ($(AT_INPUT_WIDTH), 192)
	IMAGE=$(CURDIR)/images/ILSVRC2012_val_00011158_192.ppm
endif
ifeq ($(AT_INPUT_WIDTH), 160)
	IMAGE=$(CURDIR)/images/ILSVRC2012_val_00011158_160.ppm
endif
ifeq ($(AT_INPUT_WIDTH), 128)
	IMAGE=$(CURDIR)/images/ILSVRC2012_val_00011158_128.ppm
endif


io=host

QUANT_BITS=8
BUILD_DIR=BUILD
MODEL_SQ8=1


FREQ_FC?=150000000
FREQ_CL?=150000000


$(info Building GAP8 mode with $(QUANT_BITS) bit quantization)

NNTOOL_SCRIPT=models/nntool_script
MODEL_SUFFIX = _SQ8BIT
TRAINED_TFLITE_MODEL=models/$(MODEL_PREFIX).tflite

include common/model_decl.mk

# Here we set the memory allocation for the generated kernels
# REMEMBER THAT THE L1 MEMORY ALLOCATION MUST INCLUDE SPACE
# FOR ALLOCATED STACKS!
CLUSTER_STACK_SIZE=4028
CLUSTER_SLAVE_STACK_SIZE=1024
TOTAL_STACK_SIZE=$(shell expr $(CLUSTER_STACK_SIZE) \+ $(CLUSTER_SLAVE_STACK_SIZE) \* 7)
MODEL_L1_MEMORY=$(shell expr 60000 \- $(TOTAL_STACK_SIZE))
MODEL_L2_MEMORY?=200000
MODEL_L3_MEMORY=8388608
# hram - HyperBus RAM
# qspiram - Quad SPI RAM
MODEL_L3_EXEC=hram
# hflash - HyperBus Flash
# qpsiflash - Quad SPI Flash
MODEL_L3_CONST=hflash

pulpChip = GAP
PULP_APP = imagenet
USE_PMSIS_BSP=1

APP = imagenet
APP_SRCS += main.c $(MODEL_GEN_C) $(MODEL_COMMON_SRCS) $(CNN_LIB)

APP_CFLAGS += -g -O1 -mno-memcpy -fno-tree-loop-distribute-patterns 
APP_CFLAGS += -I. -I$(MODEL_COMMON_INC) -I$(TILER_EMU_INC) -I$(TILER_INC) $(CNN_LIB_INCLUDE) -I$(MODEL_BUILD) -I$(MODEL_HEADERS)
APP_CFLAGS += -DAT_MODEL_PREFIX=$(MODEL_PREFIX) $(MODEL_SIZE_CFLAGS)
APP_CFLAGS += -DSTACK_SIZE=$(CLUSTER_STACK_SIZE) -DSLAVE_STACK_SIZE=$(CLUSTER_SLAVE_STACK_SIZE)
APP_CFLAGS += -DAT_IMAGE=$(IMAGE) -DPERF -DMODEL_ID=$(MODEL_ID) -DFREQ_FC=$(FREQ_FC) -DFREQ_CL=$(FREQ_CL)
APP_CFLAGS += -DAT_CONSTRUCT=$(AT_CONSTRUCT) -DAT_DESTRUCT=$(AT_DESTRUCT) -DAT_CNN=$(AT_CNN) -DAT_L3_ADDR=$(AT_L3_ADDR)

READFS_FILES=$(abspath $(MODEL_TENSORS))
PLPBRIDGE_FLAGS += -f

# all depends on the model
all:: model

clean:: clean_model

include common/model_rules.mk
$(info APP_SRCS... $(APP_SRCS))
$(info APP_CFLAGS... $(APP_CFLAGS))
include $(RULES_DIR)/pmsis_rules.mk

