# Copyright (C) 2017 GreenWaves Technologies
# All rights reserved.

# This software may be modified and distributed under the terms
# of the BSD license.  See the LICENSE file for details.

ifndef GAP_SDK_HOME
  $(error Source sourceme in gap_sdk first)
endif

include common.mk
QUANT_FLAG ?= -q

ifeq ($(AT_INPUT_WIDTH), 224)
	IMAGE=$(CURDIR)/images/ILSVRC2012_val_00011158_224.ppm
endif
ifeq ($(AT_INPUT_WIDTH), 192)
	IMAGE=$(CURDIR)/images/ILSVRC2012_val_00011158_192.ppm
endif
ifeq ($(AT_INPUT_WIDTH), 160)
	IMAGE=$(CURDIR)/images/ILSVRC2012_val_00011158_160.ppm
endif
ifeq ($(AT_INPUT_WIDTH), 144)
	IMAGE=$(CURDIR)/images/ILSVRC2012_val_00047406_144.ppm
endif
ifeq ($(AT_INPUT_WIDTH), 128)
	IMAGE=$(CURDIR)/images/ILSVRC2012_val_00011158_128.ppm
endif
ifeq ($(AT_INPUT_WIDTH), 96)
	IMAGE=$(CURDIR)/images/ILSVRC2012_val_00011158_96.ppm
endif

io?=host

QUANT_BITS=8
BUILD_DIR=BUILD
$(info Building GAP8 mode with $(QUANT_BITS) bit quantization)

MODEL_SQ8=1 # use scale based quantization (tflite-like)
MODEL_NE16 ?= 0
MODEL_HWC ?= 0

NNTOOL_SCRIPT?=models/nntool_scripts/nntool_script
MODEL_SUFFIX=_SQ8BIT
TRAINED_TFLITE_MODEL=models/tflite_models/$(MODEL_PREFIX).tflite

ifeq ($(MODEL_NE16), 1)
	ifeq ($(MODEL_ID), 33)
	NNTOOL_SCRIPT=models/nntool_scripts/nntool_script_mbv3_small_ne16	
	else
	NNTOOL_SCRIPT=models/nntool_scripts/nntool_script_ne16	
	endif
	MODEL_SUFFIX = _NE16
	APP_CFLAGS += -Wno-discarded-qualifiers -DMODEL_NE16
else ifeq ($(MODEL_HWC), 1)
	NNTOOL_SCRIPT=models/nntool_scripts/nntool_script_hwc
	APP_CFLAGS += -DMODEL_HWC
endif
ifeq ($(MODEL_FP16), 1)
	ifeq ($(MODEL_HWC), 1)
		APP_CFLAGS += -DMODEL_HWC
		NNTOOL_SCRIPT=models/nntool_scripts/nntool_script_hwc_fp16
	else
		NNTOOL_SCRIPT = models/nntool_scripts/nntool_script_fp16
	endif
	CLUSTER_STACK_SIZE=6096
	QUANT_BITS = 0
	MODEL_SUFFIX = _FP16
	APP_CFLAGS += -DFLOAT16
	MAIN = main_fp16.c
endif

include common/model_decl.mk

# Here we set the default memory allocation for the generated kernels
# REMEMBER THAT THE L1 MEMORY ALLOCATION MUST INCLUDE SPACE
# FOR ALLOCATED STACKS!
ifeq '$(TARGET_CHIP_FAMILY)' 'GAP9'
	CLUSTER_STACK_SIZE?=2048
	CLUSTER_SLAVE_STACK_SIZE?=512
	TOTAL_STACK_SIZE = $(shell expr $(CLUSTER_STACK_SIZE) \+ $(CLUSTER_SLAVE_STACK_SIZE) \* 8)
	FREQ_CL?=50
	FREQ_FC?=50
	FREQ_PE?=50
	MODEL_L1_MEMORY=$(shell expr 128000 \- $(TOTAL_STACK_SIZE))
	MODEL_L2_MEMORY?=1350000
	MODEL_L3_MEMORY=8000000
	USE_PRIVILEGED_FLASH?=1
else
	CLUSTER_STACK_SIZE?=6144
	CLUSTER_SLAVE_STACK_SIZE?=512
	TOTAL_STACK_SIZE = $(shell expr $(CLUSTER_STACK_SIZE) \+ $(CLUSTER_SLAVE_STACK_SIZE) \* 7)
	ifeq '$(TARGET_CHIP)' 'GAP8_V3'
		FREQ_CL?=175
	else
		FREQ_CL?=50
	endif
	FREQ_FC?=250
	FREQ_PE?=250
	MODEL_L1_MEMORY=$(shell expr 60000 \- $(TOTAL_STACK_SIZE))
	MODEL_L2_MEMORY?=300000
	MODEL_L3_MEMORY=8000000
	USE_PRIVILEGED_FLASH=0
endif

ifeq ($(USE_PRIVILEGED_FLASH), 1)
MODEL_SEC_L3_FLASH=AT_MEM_L3_MRAMFLASH
else
MODEL_SEC_L3_FLASH=
endif

FLASH_TYPE ?= DEFAULT
RAM_TYPE   ?= DEFAULT

ifeq '$(FLASH_TYPE)' 'HYPER'
  MODEL_L3_FLASH=AT_MEM_L3_HFLASH
else ifeq '$(FLASH_TYPE)' 'MRAM'
  MODEL_L3_FLASH=AT_MEM_L3_MRAMFLASH
  READFS_FLASH = target/chip/soc/mram
else ifeq '$(FLASH_TYPE)' 'QSPI'
  MODEL_L3_FLASH=AT_MEM_L3_QSPIFLASH
else ifeq '$(FLASH_TYPE)' 'OSPI'
  MODEL_L3_FLASH=AT_MEM_L3_OSPIFLASH
else ifeq '$(FLASH_TYPE)' 'DEFAULT'
  MODEL_L3_FLASH=AT_MEM_L3_DEFAULTFLASH
endif

ifeq '$(RAM_TYPE)' 'HYPER'
  MODEL_L3_RAM=AT_MEM_L3_HRAM
else ifeq '$(RAM_TYPE)' 'QSPI'
  MODEL_L3_RAM=AT_MEM_L3_QSPIRAM
else ifeq '$(RAM_TYPE)' 'OSPI'
  MODEL_L3_RAM=AT_MEM_L3_OSPIRAM
else ifeq '$(RAM_TYPE)' 'DEFAULT'
  MODEL_L3_RAM=AT_MEM_L3_DEFAULTRAM
endif

# ram - Model input from ram
# l2  - Model input from l2 memory
MODEL_INPUT=l2


pulpChip = GAP
PULP_APP = imagenet
USE_PMSIS_BSP=1
#PMSIS_OS?=pulpos

APP = imagenet
MAIN ?= main.c
APP_SRCS += $(MAIN) $(MODEL_GEN_C) $(MODEL_EXPRESSIONS) $(MODEL_COMMON_SRCS) $(CNN_LIB)

APP_CFLAGS += -gdwarf-2 -g -O3 -mno-memcpy -fno-tree-loop-distribute-patterns -fstack-usage
# list of includes file
APP_CFLAGS += -I. -I$(GAP_SDK_HOME)/utils/power_meas_utils -I$(MODEL_COMMON_INC) -I$(TILER_EMU_INC) -I$(TILER_INC) $(CNN_LIB_INCLUDE) -I$(MODEL_BUILD) -I$(MODEL_HEADERS)
# pass also macro defines to the compiler
APP_CFLAGS += -DAT_MODEL_PREFIX=$(MODEL_PREFIX) $(MODEL_SIZE_CFLAGS)
APP_CFLAGS += -DSTACK_SIZE=$(CLUSTER_STACK_SIZE) -DSLAVE_STACK_SIZE=$(CLUSTER_SLAVE_STACK_SIZE)
APP_CFLAGS += -DAT_IMAGE=$(IMAGE) -DPERF -DMODEL_ID=$(MODEL_ID) -DFREQ_FC=$(FREQ_FC) -DFREQ_CL=$(FREQ_CL) -DFREQ_PE=$(FREQ_PE)
APP_CFLAGS += -DAT_CONSTRUCT=$(AT_CONSTRUCT) -DAT_DESTRUCT=$(AT_DESTRUCT) -DAT_CNN=$(AT_CNN) -DAT_L3_ADDR=$(AT_L3_ADDR) -DAT_L3_2_ADDR=$(AT_L3_2_ADDR)

ifneq '$(platform)' 'gvsoc'
ifdef MEAS
APP_CFLAGS += -DGPIO_MEAS
endif
endif

# Option to not read image (faster)
ifdef FAKE_INPUT
APP_CFLAGS += -DFAKE_INPUT
endif

#VOLTAGE?=800
ifdef VOLTAGE
	APP_CFLAGS += -DVOLTAGE=$(VOLTAGE)
endif

# this line is needed to flash into the chip the model tensors
# and other constants needed by the Autotiler
READFS_FILES=$(abspath $(MODEL_TENSORS))
#PLPBRIDGE_FLAGS += -f
ifneq ($(MODEL_SEC_L3_FLASH), )
  runner_args += --flash-property=$(CURDIR)/$(MODEL_SEC_TENSORS)@mram:readfs:files
endif

build:: model

clean:: clean_model

clean_at_model::
	$(RM) $(MODEL_GEN_C)
	$(RM) $(MODEL_GEN_EXE)

nntool_predict: $(MODEL_STATE)
	python models/predict_nntool.py $(MODEL_STATE)

TFLITE_PYSCRIPT= models/tflite_inference.py
test_tflite:
	python $(TFLITE_PYSCRIPT) -t $(TRAINED_TFLITE_MODEL) -i $(IMAGE)

DATASET_PATH=
test_accuracy_nntool:
	python models/test_accuracy_tflite.py $(MODEL_STATE) $(DATASET_PATH)

include common/model_rules.mk
$(info APP_SRCS... $(APP_SRCS))
$(info APP_CFLAGS... $(APP_CFLAGS))
include $(RULES_DIR)/pmsis_rules.mk

