
#ifndef __IMAGENET_H__
#define __IMAGENET_H__

#include "Gap.h"
#define __PREFIX(x) mobilenet_v1_0_5_128_quant ## x
extern AT_HYPERFLASH_FS_EXT_ADDR_TYPE __PREFIX(_L3_Flash);
extern AT_HYPERFLASH_FS_EXT_ADDR_TYPE __PREFIX(_L3_PrivilegedFlash);

#endif
