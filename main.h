#ifndef __IMAGENET_H__
#define __IMAGENET_H__

#if MODEL_ID==0
	#include "mobilenet_v1_1_0_224_quant.h"
	#include "mobilenet_v1_1_0_224_quantKernels.h"
#elif MODEL_ID==1
	#include "mobilenet_v1_1_0_192_quant.h"
	#include "mobilenet_v1_1_0_192_quantKernels.h"
#elif MODEL_ID==2
	#include "mobilenet_v1_1_0_160_quant.h"
	#include "mobilenet_v1_1_0_160_quantKernels.h"
#elif MODEL_ID==3
	#include "mobilenet_v1_1_0_128_quant.h"
	#include "mobilenet_v1_1_0_128_quantKernels.h"
#elif MODEL_ID==4
	#include "mobilenet_v1_0_75_224_quant.h"
	#include "mobilenet_v1_0_75_224_quantKernels.h"
#elif MODEL_ID==5
	#include "mobilenet_v1_0_75_192_quant.h"
	#include "mobilenet_v1_0_75_192_quantKernels.h"
#elif MODEL_ID==6
	#include "mobilenet_v1_0_75_160_quant.h"
	#include "mobilenet_v1_0_75_160_quantKernels.h"
#elif MODEL_ID==7
	#include "mobilenet_v1_0_75_128_quant.h"
	#include "mobilenet_v1_0_75_128_quantKernels.h"
#elif MODEL_ID==8
	#include "mobilenet_v1_0_5_224_quant.h"
	#include "mobilenet_v1_0_5_224_quantKernels.h"
#elif MODEL_ID==9
	#include "mobilenet_v1_0_5_192_quant.h"
	#include "mobilenet_v1_0_5_192_quantKernels.h"
#elif MODEL_ID==10
	#include "mobilenet_v1_0_5_160_quant.h"
	#include "mobilenet_v1_0_5_160_quantKernels.h"
#elif MODEL_ID==11
	#include "mobilenet_v1_0_5_128_quant.h"
	#include "mobilenet_v1_0_5_128_quantKernels.h"
#elif MODEL_ID==12
	#include "mobilenet_v1_0_25_224_quant.h"
	#include "mobilenet_v1_0_25_224_quantKernels.h"
#elif MODEL_ID==13
	#include "mobilenet_v1_0_25_192_quant.h"
	#include "mobilenet_v1_0_25_192_quantKernels.h"
#elif MODEL_ID==14
	#include "mobilenet_v1_0_25_160_quant.h"
	#include "mobilenet_v1_0_25_160_quantKernels.h"
#elif MODEL_ID==15
	#include "mobilenet_v1_0_25_128_quant.h"
	#include "mobilenet_v1_0_25_128_quantKernels.h"
#elif MODEL_ID==16
	#include "mobilenet_v2_1_0_224_quant.h"
	#include "mobilenet_v2_1_0_224_quantKernels.h"
#endif

#include "Gap.h"

extern AT_HYPERFLASH_FS_EXT_ADDR_TYPE AT_FLASH_ADDR;

#endif