# Copyright (c) 2022 GreenWaves Technologies SAS
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of GreenWaves Technologies SAS nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

cmake_minimum_required(VERSION 3.16)

###############################################################################
# Application related definitions
###############################################################################

set(TARGET_NAME         "mobilenet")
set(MAIN                main.c)

###############################################################################
# CMake pre initialization
###############################################################################

include($ENV{GAP_SDK_HOME}/utils/cmake/setup.cmake)

set(APP_MSG_PREFIX "[${BoldRed}${TARGET_NAME}${ColourReset}]")

###############################################################################
# Application's kconfig options
###############################################################################

include(${CMAKE_CURRENT_SOURCE_DIR}/common.cmake)
model_choice()

if(DEFINED CONFIG_MODEL_SQ8_HWC)
    message(STATUS "${APP_MSG_PREFIX} >> Building SQ8 HWC MobileNet model <<")
    set(CONFIG_NNTOOL_SCRIPT_PATH models/nntool_scripts/nntool_script_hwc)
    set(MODEL_SUFFIX _sq8)

elseif(DEFINED CONFIG_MODEL_SQ8)
    message(STATUS "${APP_MSG_PREFIX} >> Building SQ8 MobileNet model <<")
    set(CONFIG_NNTOOL_SCRIPT_PATH models/nntool_scripts/nntool_script)
    set(MODEL_SUFFIX _sq8)

elseif(DEFINED CONFIG_MODEL_FP16)
    message(STATUS "${APP_MSG_PREFIX} >> Building FP16 MobileNet model <<")
    set(CONFIG_NNTOOL_SCRIPT_PATH models/nntool_scripts/nntool_script_fp16)
    set(MODEL_SUFFIX _fp16)
    set(MAIN main_fp16.c)

elseif(DEFINED CONFIG_MODEL_FP16_HWC)
    message(STATUS "${APP_MSG_PREFIX} >> Building FP16 HWC MobileNet model <<")
    set(CONFIG_NNTOOL_SCRIPT_PATH models/nntool_scripts/nntool_script_hwc_fp16)
    set(MODEL_SUFFIX _fp16)
    set(MAIN main_fp16.c)

elseif(DEFINED CONFIG_MODEL_NE16)
    message(STATUS "${APP_MSG_PREFIX} >> Building NE16 MobileNet model <<")
    set(CONFIG_NNTOOL_SCRIPT_PATH models/nntool_scripts/nntool_script_ne16)
    set(MODEL_SUFFIX _ne16)


endif()

set(IMAGE images/ILSVRC2012_val_00011158_${AT_INPUT_WIDTH}.ppm)

###############################################################################
# NNTool Variables 
###############################################################################

if (CONFIG_USE_PRIVILEGED_MRAM)
    message(STATUS "${APP_MSG_PREFIX} Selected MRAM Privileged flash")
    list(APPEND NNTOOLSCRIPT_FLAGS -DMODEL_SEC_L3_FLASH=AT_MEM_L3_MRAMFLASH)
else()
    list(APPEND NNTOOLSCRIPT_FLAGS -DMODEL_SEC_L3_FLASH=)
endif()
autotiler_define_gen_names(${TARGET_NAME})
nntool_setup(${TARGET_NAME})
autotiler_setup(${TARGET_NAME})

###############################################################################
# Application dependencies
###############################################################################

list(APPEND TARGET_SRCS ${MAIN}
                        ${CNN_LIB}
                        ${COMMON_MODEL_BUILDDIR}/${KERNEL_C}
)

list(APPEND TARGET_INCS -I${TILER_INC}
                        -I${TILER_EMU_INC}
                        -I${GAP_SDK_HOME}/libs/gap_lib/include
                          ${CNN_LIB_INCLUDE}
                        -I${COMMON_MODEL_BUILDDIR}
                        -I${CMAKE_CURRENT_SOURCE_DIR}
                        -I${GAP_SDK_HOME}/utils/power_meas_utils)

list(APPEND TARGET_CFLAGS   -gdwarf-2
                            -gstrict-dwarf
                            -O3
                            -mno-memcpy
                            -fno-tree-loop-distribute-patterns)

math(EXPR FREQ_CL_MHZ "${CONFIG_FREQUENCY_CLUSTER}/1000/1000")
math(EXPR FREQ_FC_MHZ "${CONFIG_FREQUENCY_FC}/1000/1000")
math(EXPR FREQ_PE_MHZ "${CONFIG_FREQUENCY_PERIPH}/1000/1000")
list(APPEND TARGET_PREPROCESSOR -DPERF
                                -DAT_MODEL_PREFIX=${MODEL_NAME}
                                -DSTACK_SIZE=${CONFIG_CL_MASTER_CORE_STACK_SIZE}
                                -DSLAVE_STACK_SIZE=${CONFIG_CL_SLAVE_CORE_STACK_SIZE}
                                -DAT_IMAGE=${CMAKE_CURRENT_SOURCE_DIR}/${IMAGE}
                                -DAT_INPUT_HEIGHT=${AT_INPUT_WIDTH}
                                -DAT_INPUT_WIDTH=${AT_INPUT_HEIGHT}
                                -DAT_INPUT_COLORS=${AT_INPUT_COLORS}
                                -DFREQ_CL=${FREQ_CL_MHZ}
                                -DFREQ_FC=${FREQ_FC_MHZ}
                                -DFREQ_PE=${FREQ_PE_MHZ}
                                -DAT_CONSTRUCT=${AT_CONSTRUCT}
                                -DAT_DESTRUCT=${AT_DESTRUCT}
                                -DAT_CNN=${AT_CNN})
if (DEFINED PERF_CI)
list(APPEND TARGET_PREPROCESSOR -DPERF_CI=${PERF_CI})
endif()
if (CONFIG_MODEL_REENTRANT_MODE)
list(APPEND TARGET_PREPROCESSOR -DREENTRANT)
endif()
if (CONFIG_GPIO_MEAS)
list(APPEND TARGET_PREPROCESSOR -DGPIO_MEAS)
endif()
if (CONFIG_SILENT)
list(APPEND TARGET_PREPROCESSOR -DSILENT)
endif()


project(${TARGET_NAME} C ASM)
add_executable(${TARGET_NAME} ${TARGET_SRCS})

target_compile_options(${TARGET_NAME} PUBLIC    ${TARGET_CFLAGS} 
                                                ${TARGET_INCS}
                                                ${TARGET_PREPROCESSOR})


###############################################################################
# CMake post initialization
###############################################################################
setupos(${TARGET_NAME})

