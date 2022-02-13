# Copyright (C) 2017 GreenWaves Technologies
# All rights reserved.

# This software may be modified and distributed under the terms
# of the BSD license.  See the LICENSE file for details.

ifndef GAP_SDK_HOME
  $(error Source sourceme in gap_sdk first)
endif

#include common.mk
MODEL_ID?=0
MODEL_PREFIX?=prefix
AT_INPUT_WIDTH?=224
AT_INPUT_HEIGHT?=224
AT_INPUT_COLORS?=1
NNTOOL_SCRIPT=prefix.nntool
AT_CONSTRUCT = $(MODEL_PREFIX)CNN_Construct
AT_DESTRUCT = $(MODEL_PREFIX)CNN_Destruct
AT_CNN = $(MODEL_PREFIX)CNN
AT_L3_ADDR = $(MODEL_PREFIX)_L3_Flash

QUANT_FLAG ?= -q

IMAGE=$(CURDIR)/images/ILSVRC2012_val_00011158_$(AT_INPUT_WIDTH).ppm

io=host

QUANT_BITS=8
BUILD_DIR=BUILD
$(info Building GAP8 mode with $(QUANT_BITS) bit quantization)

MODEL_SQ8=1 # use scale based quantization (tflite-like)

NNTOOL_SCRIPT?=models/nntool_scripts/nntool_script
MODEL_SUFFIX=_SQ8BIT
TRAINED_ONNX_MODEL=$(MODEL_PREFIX).onnx

MODEL_HEADERS = headers
MODEL_BUILD = BUILD_MODEL$(MODEL_SUFFIX)
MODEL_ONNX = $(MODEL_BUILD)/$(MODEL_PREFIX).onnx
TENSORS_DIR = $(MODEL_BUILD)/tensors
MODEL_TENSORS = $(MODEL_BUILD)/$(MODEL_PREFIX)_L3_Flash_Const.dat
MODEL_STATE = $(MODEL_BUILD)/$(MODEL_PREFIX).json
MODEL_SRC = $(MODEL_PREFIX)Model.c
MODEL_GEN = $(MODEL_BUILD)/$(MODEL_PREFIX)Kernels 
MODEL_GEN_C = $(addsuffix .c, $(MODEL_GEN))
MODEL_GEN_CLEAN = $(MODEL_GEN_C) $(addsuffix .h, $(MODEL_GEN))
MODEL_GEN_EXE = $(MODEL_BUILD)/GenTile
MODEL_GENFLAGS_EXTRA =
EXTRA_GENERATOR_SRC =
IMAGES = images
RM=rm -f
NNTOOL=nntool
include $(RULES_DIR)/at_common_decl.mk
$(info GEN ... $(CNN_GEN))

# Here we set the default memory allocation for the generated kernels
# REMEMBER THAT THE L1 MEMORY ALLOCATION MUST INCLUDE SPACE
# FOR ALLOCATED STACKS!
CLUSTER_STACK_SIZE?=6096
CLUSTER_SLAVE_STACK_SIZE?=1024
TOTAL_STACK_SIZE = $(shell expr $(CLUSTER_STACK_SIZE) \+ $(CLUSTER_SLAVE_STACK_SIZE) \* 7)
ifeq '$(TARGET_CHIP_FAMILY)' 'GAP9'
	FREQ_CL?=50
	FREQ_FC?=50
	MODEL_L1_MEMORY=$(shell expr 125000 \- $(TOTAL_STACK_SIZE))
	MODEL_L2_MEMORY=1300000
	MODEL_L3_MEMORY=8388608
else
	ifeq '$(TARGET_CHIP)' 'GAP8_V3'
		FREQ_CL?=175
	else
		FREQ_CL?=50
	endif
	FREQ_FC?=250
	MODEL_L1_MEMORY=$(shell expr 60000 \- $(TOTAL_STACK_SIZE))
	MODEL_L2_MEMORY?=300000
	MODEL_L3_MEMORY=8000000
endif

# hram - HyperBus RAM
# qspiram - Quad SPI RAM
MODEL_L3_EXEC=hram
# hflash - HyperBus Flash
# qpsiflash - Quad SPI Flash
MODEL_L3_CONST=hflash
# ram - Model input from ram
# l2  - Model input from l2 memory
MODEL_INPUT=ram


pulpChip = GAP
PULP_APP = imagenet
USE_PMSIS_BSP=1
PMSIS_OS=pulpos

APP = imagenet
MAIN ?= main.c
APP_SRCS += $(MAIN) $(MODEL_GEN_C) $(MODEL_COMMON_SRCS) $(CNN_LIB) cam/cam.c spi-wifi/spi_wifi.c

APP_CFLAGS += -g -O3 -mno-memcpy -fno-tree-loop-distribute-patterns
# list of includes file
APP_CFLAGS += -I. -I$(MODEL_COMMON_INC) -I$(TILER_EMU_INC) -I$(TILER_INC) $(CNN_LIB_INCLUDE) -I$(MODEL_BUILD) -I$(MODEL_HEADERS)
# pass also macro defines to the compiler
APP_CFLAGS += -DAT_MODEL_PREFIX=$(MODEL_PREFIX) $(MODEL_SIZE_CFLAGS)
APP_CFLAGS += -DSTACK_SIZE=$(CLUSTER_STACK_SIZE) -DSLAVE_STACK_SIZE=$(CLUSTER_SLAVE_STACK_SIZE)
APP_CFLAGS += -DAT_IMAGE=$(IMAGE) -DPERF -DMODEL_ID=$(MODEL_ID) -DFREQ_FC=$(FREQ_FC) -DFREQ_CL=$(FREQ_CL)
APP_CFLAGS += -DAT_CONSTRUCT=$(AT_CONSTRUCT) -DAT_DESTRUCT=$(AT_DESTRUCT) -DAT_CNN=$(AT_CNN) -DAT_L3_ADDR=$(AT_L3_ADDR)

HAVE_CAMERA?=0
HAVE_LCD?=0
ifeq ($(HAVE_CAMERA), 1)
	APP_CFLAGS += -DHAVE_CAMERA
endif
ifeq ($(HAVE_LCD), 1)
	APP_CFLAGS += -DHAVE_LCD
endif

MODEL_L3_RAM=AT_MEM_L3_HRAM

MODEL_L3_FLASH=AT_MEM_L3_HFLASH

MODEL_INPUT=AT_MEM_L3_HRAM

# this line is needed to flash into the chip the model tensors
# and other constants needed by the Autotiler
READFS_FILES=$(abspath $(MODEL_TENSORS))
PLPBRIDGE_FLAGS += -f

# all depends on the model
all:: model

clean:: clean_model

clean_at_model::
	$(RM) $(MODEL_GEN_C)

#include common/model_rules.mk

USE_DISP=1

ifdef USE_DISP
  SDL_FLAGS= -lSDL2 -lSDL2_ttf -DAT_DISPLAY
else
  SDL_FLAGS=
endif

ifdef MODEL_L1_MEMORY
  MODEL_GEN_EXTRA_FLAGS += --L1 $(MODEL_L1_MEMORY)
endif

ifdef MODEL_L2_MEMORY
  MODEL_GEN_EXTRA_FLAGS += --L2 $(MODEL_L2_MEMORY)
endif

ifdef MODEL_L3_MEMORY
  MODEL_GEN_EXTRA_FLAGS += --L3 $(MODEL_L3_MEMORY)
endif


$(MODEL_BUILD):
	mkdir $(MODEL_BUILD)

$(MODEL_ONNX): $(TRAINED_ONNX_MODEL) | $(MODEL_BUILD)
	cp $< $@

$(MODEL_STATE): $(MODEL_ONNX) $(IMAGES) | $(MODEL_BUILD)
	echo "GENERATING NNTOOL STATE FILE"
	$(NNTOOL) -s $(NNTOOL_SCRIPT) $< $(QUANT_FLAG)

nntool_state: $(MODEL_STATE)

# Runs NNTOOL with its state file to generate the autotiler model code
$(MODEL_BUILD)/$(MODEL_SRC): $(MODEL_STATE) $(MODEL_ONNX) | $(MODEL_BUILD)
	echo "GENERATING AUTOTILER MODEL"
	$(NNTOOL) -g -M $(MODEL_BUILD) -m $(MODEL_SRC) -T $(TENSORS_DIR) $(MODEL_GENFLAGS_EXTRA) $<

nntool_gen: $(MODEL_BUILD)/$(MODEL_SRC)

# Build the code generator from the model code
$(MODEL_GEN_EXE): $(CNN_GEN) $(MODEL_BUILD)/$(MODEL_SRC) $(EXTRA_GENERATOR_SRC) | $(MODEL_BUILD)
	echo "COMPILING AUTOTILER MODEL"
	gcc -g -o $(MODEL_GEN_EXE) -I. -I$(TILER_EMU_INC) -I$(TILER_INC) $(CNN_GEN_INCLUDE) $(CNN_LIB_INCLUDE) $^ $(TILER_LIB) $(SDL_FLAGS)

compile_model: $(MODEL_GEN_EXE)

# Run the code generator to generate GAP graph and kernel code
$(MODEL_GEN_C): $(MODEL_GEN_EXE)
	echo "RUNNING AUTOTILER MODEL"
	$(MODEL_GEN_EXE) -o $(MODEL_BUILD) -c $(MODEL_BUILD) $(MODEL_GEN_EXTRA_FLAGS)

# A phony target to simplify including this in the main Makefile
model: $(MODEL_GEN_C)

clean_model:
	$(RM) $(MODEL_GEN_EXE)
	$(RM) -rf $(MODEL_BUILD)

clean_train:
	$(RM) -rf $(MODEL_TRAIN_BUILD)

clean_images:
	$(RM) -rf $(IMAGES)

test_images: $(IMAGES)

.PHONY: model clean_model clean_train test_images clean_images train nntool_gen nntool_state tflite compile_model

$(info APP_SRCS... $(APP_SRCS))
$(info APP_CFLAGS... $(APP_CFLAGS))
include $(RULES_DIR)/pmsis_rules.mk
