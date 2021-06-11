# Copyright (C) 2020 GreenWaves Technologies
# All rights reserved.

# This software may be modified and distributed under the terms
# of the BSD license.  See the LICENSE file for details.


NNTOOL_SCRIPT?=../models/nntool_scripts/nntool_script_emul
include ../common.mk

QUANT_BITS = 8
MODEL_SQ8 = 1
MODEL_SUFFIX=_SQ$(QUANT_BITS)BIT_EMUL

$(info Building emulation mode with 8 bit quantization)

# The training of the model is slightly different depending on
# the quantization. This is because in 8 bit mode we used signed
# 8 bit so the input to the model needs to be shifted 1 bit

TRAINED_TFLITE_MODEL=../models/tflite_models/$(MODEL_PREFIX).tflite

include ../common/model_decl.mk
IMAGES = ../images

MAIN ?= main_emul.c

MODEL_GEN_EXTRA_FLAGS= -f $(MODEL_BUILD)
MODEL_GENFLAGS_EXTRA+=
CC = gcc
OPTIMIZATION?=-O3
CFLAGS += -g -m32 $(OPTIMIZATION) -D__EMUL__ -DMODEL_ID=$(MODEL_ID) -DAT_MODEL_PREFIX=$(MODEL_PREFIX) $(MODEL_SIZE_CFLAGS)
CFLAGS += -DAT_CONSTRUCT=$(AT_CONSTRUCT) -DAT_DESTRUCT=$(AT_DESTRUCT) -DAT_CNN=$(AT_CNN) -DAT_L3_ADDR=$(AT_L3_ADDR) -DSILENT
INCLUDES = -I../ -I$(TILER_EMU_INC) -I$(TILER_INC) $(CNN_LIB_INCLUDE) -I$../$(MODEL_BUILD) -I$(MODEL_COMMON_INC) -I../$(MODEL_HEADERS)
LFLAGS =
LIBS =
SRCS = $(MAIN) $(MODEL_GEN_C) $(MODEL_COMMON_SRCS) $(CNN_LIB)
$(info CNN_LIB++ $(CNN_LIB))
$(info SRCS++ $(SRCS))
BUILD_DIR = BUILD_EMUL

OBJS = $(patsubst %.c, $(BUILD_DIR)/%.o, $(SRCS))

EXE = $(MODEL_PREFIX)_emul
# Here we set the memory allocation for the generated kernels
# REMEMBER THAT THE L1 MEMORY ALLOCATION MUST INCLUDE SPACE
# FOR ALLOCATED STACKS!
CLUSTER_STACK_SIZE?=2048
CLUSTER_SLAVE_STACK_SIZE?=1024
TOTAL_STACK_SIZE?=$(shell expr $(CLUSTER_STACK_SIZE) \+ $(CLUSTER_SLAVE_STACK_SIZE) \* 7)
MODEL_L1_MEMORY?=$(shell expr 60000 \- $(TOTAL_STACK_SIZE))
MODEL_L2_MEMORY?=350000
MODEL_L3_MEMORY?=8388608

# Here we set the memory allocation for the generated kernels
# REMEMBER THAT THE L1 MEMORY ALLOCATION MUST INCLUDE SPACE
# FOR ALLOCATED STACKS!
# MODEL_L1_MEMORY=52000
# MODEL_L2_MEMORY=307200
# MODEL_L3_MEMORY=8388608
# hram - HyperBus RAM
# qspiram - Quad SPI RAM
MODEL_L3_EXEC=hram
# hflash - HyperBus Flash
# qpsiflash - Quad SPI Flash
MODEL_L3_CONST=hflash

all: model $(EXE)

$(OBJS) : $(BUILD_DIR)/%.o : %.c
	@mkdir -p $(dir $@)
	$(CC) $(CFLAGS) -c $< $(INCLUDES) -MD -MF $(basename $@).d -o $@

$(EXE): $(OBJS)
	$(CC) $(CFLAGS) -MMD -MP $(CFLAGS) $(INCLUDES) -o $(EXE) $(OBJS) $(LFLAGS) $(LIBS)

clean: clean_model
	$(RM) -r $(BUILD_DIR)
	$(RM) $(EXE)

.PHONY: depend clean

include ../common/model_rules.mk
