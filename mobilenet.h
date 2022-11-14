#ifndef __IMAGENET_H__
#define __IMAGENET_H__

#include "mobilenetKernels.h"

extern AT_HYPERFLASH_FS_EXT_ADDR_TYPE mobilenet_L3_Flash;
extern AT_HYPERFLASH_FS_EXT_ADDR_TYPE mobilenet_L3_PrivilegedFlash;

#include "Gap.h"
#include "gaplib/ImgIO.h"
#include "measurments_utils.h"

#ifdef __EMUL__
#include <sys/types.h>
#include <unistd.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <sys/param.h>
#include <string.h>
#endif

#endif
