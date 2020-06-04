# Copyright (C) 2020 GreenWaves Technologies
# All rights reserved.

# This software may be modified and distributed under the terms
# of the BSD license.  See the LICENSE file for details.



#### Model List #####
MODEL_ID?=0


ifeq ($(MODEL_ID), 0)
	MODEL_PREFIX?=mobilenet_v1_1_0_224_quant
	AT_INPUT_WIDTH?=224
	AT_INPUT_HEIGHT?=224
	AT_INPUT_COLORS?=3
endif

ifeq ($(MODEL_ID), 1)
	MODEL_PREFIX?=mobilenet_v1_1_0_192_quant
	AT_INPUT_WIDTH?=192
	AT_INPUT_HEIGHT?=192
	AT_INPUT_COLORS?=3
endif

ifeq ($(MODEL_ID), 2)
	MODEL_PREFIX?=mobilenet_v1_1_0_160_quant
	AT_INPUT_WIDTH?=160
	AT_INPUT_HEIGHT?=160
	AT_INPUT_COLORS?=3
endif

ifeq ($(MODEL_ID), 3)
	MODEL_PREFIX?=mobilenet_v1_1_0_128_quant
	AT_INPUT_WIDTH?=128
	AT_INPUT_HEIGHT?=128
	AT_INPUT_COLORS?=3
endif

ifeq ($(MODEL_ID), 4)
	MODEL_PREFIX?=mobilenet_v1_0_75_224_quant
	AT_INPUT_WIDTH?=224
	AT_INPUT_HEIGHT?=224
	AT_INPUT_COLORS?=3
endif

ifeq ($(MODEL_ID), 5)
	MODEL_PREFIX?=mobilenet_v1_0_75_192_quant
	AT_INPUT_WIDTH?=192
	AT_INPUT_HEIGHT?=192
	AT_INPUT_COLORS?=3
endif

ifeq ($(MODEL_ID), 6)
	MODEL_PREFIX?=mobilenet_v1_0_75_160_quant
	AT_INPUT_WIDTH?=160
	AT_INPUT_HEIGHT?=160
	AT_INPUT_COLORS?=3
endif

ifeq ($(MODEL_ID), 7)
	MODEL_PREFIX?=mobilenet_v1_0_75_128_quant
	AT_INPUT_WIDTH?=128
	AT_INPUT_HEIGHT?=128
	AT_INPUT_COLORS?=3
endif

ifeq ($(MODEL_ID), 8)
	MODEL_PREFIX?=mobilenet_v1_0_5_224_quant
	AT_INPUT_WIDTH?=224
	AT_INPUT_HEIGHT?=224
	AT_INPUT_COLORS?=3
endif

ifeq ($(MODEL_ID), 9)
	MODEL_PREFIX?=mobilenet_v1_0_5_192_quant
	AT_INPUT_WIDTH?=192
	AT_INPUT_HEIGHT?=192
	AT_INPUT_COLORS?=3
endif

ifeq ($(MODEL_ID), 10)
	MODEL_PREFIX?=mobilenet_v1_0_5_160_quant
	AT_INPUT_WIDTH?=160
	AT_INPUT_HEIGHT?=160
	AT_INPUT_COLORS?=3
endif

ifeq ($(MODEL_ID), 11)
	MODEL_PREFIX?=mobilenet_v1_0_5_128_quant
	AT_INPUT_WIDTH?=128
	AT_INPUT_HEIGHT?=128
	AT_INPUT_COLORS?=3
endif

ifeq ($(MODEL_ID), 12)
	MODEL_PREFIX?=mobilenet_v1_0_25_224_quant
	AT_INPUT_WIDTH?=224
	AT_INPUT_HEIGHT?=224
	AT_INPUT_COLORS?=3
endif

ifeq ($(MODEL_ID), 13)
	MODEL_PREFIX?=mobilenet_v1_0_25_192_quant
	AT_INPUT_WIDTH?=192
	AT_INPUT_HEIGHT?=192
	AT_INPUT_COLORS?=3
endif

ifeq ($(MODEL_ID), 14)
	MODEL_PREFIX?=mobilenet_v1_0_25_160_quant
	AT_INPUT_WIDTH?=160
	AT_INPUT_HEIGHT?=160
	AT_INPUT_COLORS?=3
endif

ifeq ($(MODEL_ID), 15)
	MODEL_PREFIX?=mobilenet_v1_0_25_128_quant
	AT_INPUT_WIDTH?=128
	AT_INPUT_HEIGHT?=128
	AT_INPUT_COLORS?=3
endif

ifeq ($(MODEL_ID), 16)
	MODEL_PREFIX?=mobilenet_v2_1_0_224_quant
	AT_INPUT_WIDTH?=224
	AT_INPUT_HEIGHT?=224
	AT_INPUT_COLORS?=3
endif

AT_CONSTRUCT = $(MODEL_PREFIX)CNN_Construct
AT_DESTRUCT = $(MODEL_PREFIX)CNN_Destruct
AT_CNN = $(MODEL_PREFIX)CNN
AT_L3_ADDR = $(MODEL_PREFIX)_L3_Flash
