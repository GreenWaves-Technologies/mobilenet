
# This macro must be executed at the beginning of the cmake build process.
macro(model_choice)
    if (${CONFIG_MODEL_ID} EQUAL 0)
        set(MODEL_NAME mobilenet_v1_1_0_224_quant)
        set(AT_INPUT_WIDTH 224)
    elseif(${CONFIG_MODEL_ID} EQUAL 1)
        set(MODEL_NAME mobilenet_v1_1_0_192_quant)
        set(AT_INPUT_WIDTH 192)
    elseif(${CONFIG_MODEL_ID} EQUAL 2)
        set(MODEL_NAME mobilenet_v1_1_0_160_quant)
        set(AT_INPUT_WIDTH 160)
    elseif(${CONFIG_MODEL_ID} EQUAL 3)
        set(MODEL_NAME mobilenet_v1_1_0_128_quant)
        set(AT_INPUT_WIDTH 128)
    elseif(${CONFIG_MODEL_ID} EQUAL 4)
        set(MODEL_NAME mobilenet_v1_0_75_224_quant)
        set(AT_INPUT_WIDTH 224)
    elseif(${CONFIG_MODEL_ID} EQUAL 5)
        set(MODEL_NAME mobilenet_v1_0_75_192_quant)
        set(AT_INPUT_WIDTH 192)
    elseif(${CONFIG_MODEL_ID} EQUAL 6)
        set(MODEL_NAME mobilenet_v1_0_75_160_quant)
        set(AT_INPUT_WIDTH 160)
    elseif(${CONFIG_MODEL_ID} EQUAL 7)
        set(MODEL_NAME mobilenet_v1_0_75_128_quant)
        set(AT_INPUT_WIDTH 128)
    elseif(${CONFIG_MODEL_ID} EQUAL 8)
        set(MODEL_NAME mobilenet_v1_0_5_224_quant)
        set(AT_INPUT_WIDTH 224)
    elseif(${CONFIG_MODEL_ID} EQUAL 9)
        set(MODEL_NAME mobilenet_v1_0_5_192_quant)
        set(AT_INPUT_WIDTH 192)
    elseif(${CONFIG_MODEL_ID} EQUAL 10)
        set(MODEL_NAME mobilenet_v1_0_5_160_quant)
        set(AT_INPUT_WIDTH 160)
    elseif(${CONFIG_MODEL_ID} EQUAL 11)
        set(MODEL_NAME mobilenet_v1_0_5_128_quant)
        set(AT_INPUT_WIDTH 128)
    elseif(${CONFIG_MODEL_ID} EQUAL 12)
        set(MODEL_NAME mobilenet_v1_0_25_224_quant)
        set(AT_INPUT_WIDTH 224)
        if (NOT CONFIG_MODEL_FP16)
            set(CONFIG_ONLY_PRIVILEGED_FLASH_USED y)
        endif()
    elseif(${CONFIG_MODEL_ID} EQUAL 13)
        set(MODEL_NAME mobilenet_v1_0_25_192_quant)
        set(AT_INPUT_WIDTH 192)
        if (NOT CONFIG_MODEL_FP16)
            set(CONFIG_ONLY_PRIVILEGED_FLASH_USED y)
        endif()
    elseif(${CONFIG_MODEL_ID} EQUAL 14)
        set(MODEL_NAME mobilenet_v1_0_25_160_quant)
        set(AT_INPUT_WIDTH 160)
        if (NOT CONFIG_MODEL_FP16)
            set(CONFIG_ONLY_PRIVILEGED_FLASH_USED y)
        endif()
    elseif(${CONFIG_MODEL_ID} EQUAL 15)
        set(MODEL_NAME mobilenet_v1_0_25_128_quant)
        set(AT_INPUT_WIDTH 128)
        if (NOT CONFIG_MODEL_FP16)
            set(CONFIG_ONLY_PRIVILEGED_FLASH_USED y)
        endif()
    elseif(${CONFIG_MODEL_ID} EQUAL 16)
        set(MODEL_NAME mobilenet_v2_1_4_224_quant)
        set(AT_INPUT_WIDTH 224)
    elseif(${CONFIG_MODEL_ID} EQUAL 17)
        set(MODEL_NAME mobilenet_v2_1_0_224_quant)
        set(AT_INPUT_WIDTH 224)
    elseif(${CONFIG_MODEL_ID} EQUAL 18)
        set(MODEL_NAME mobilenet_v2_1_0_192_quant)
        set(AT_INPUT_WIDTH 192)
    elseif(${CONFIG_MODEL_ID} EQUAL 19)
        set(MODEL_NAME mobilenet_v2_1_0_160_quant)
        set(AT_INPUT_WIDTH 160)
    elseif(${CONFIG_MODEL_ID} EQUAL 20)
        set(MODEL_NAME mobilenet_v2_1_0_128_quant)
        set(AT_INPUT_WIDTH 128)
    elseif(${CONFIG_MODEL_ID} EQUAL 21)
        set(MODEL_NAME mobilenet_v2_1_0_96_quant)
        set(AT_INPUT_WIDTH 224)
    elseif(${CONFIG_MODEL_ID} EQUAL 22)
        set(MODEL_NAME mobilenet_v2_0_75_224_quant)
        set(AT_INPUT_WIDTH 224)
    elseif(${CONFIG_MODEL_ID} EQUAL 23)
        set(MODEL_NAME mobilenet_v2_0_75_192_quant)
        set(AT_INPUT_WIDTH 192)
    elseif(${CONFIG_MODEL_ID} EQUAL 24)
        set(MODEL_NAME mobilenet_v2_0_75_160_quant)
        set(AT_INPUT_WIDTH 160)
    elseif(${CONFIG_MODEL_ID} EQUAL 25)
        set(MODEL_NAME mobilenet_v2_0_75_128_quant)
        set(AT_INPUT_WIDTH 128)
    elseif(${CONFIG_MODEL_ID} EQUAL 26)
        set(MODEL_NAME mobilenet_v2_0_75_96_quant)
        set(AT_INPUT_WIDTH 224)
    elseif(${CONFIG_MODEL_ID} EQUAL 27)
        set(MODEL_NAME mobilenet_v2_0_5_224_quant)
        set(AT_INPUT_WIDTH 224)
    elseif(${CONFIG_MODEL_ID} EQUAL 28)
        set(MODEL_NAME mobilenet_v2_0_5_192_quant)
        set(AT_INPUT_WIDTH 192)
    elseif(${CONFIG_MODEL_ID} EQUAL 29)
        set(MODEL_NAME mobile0 33net_v2_0_5_160_quant)
        set(AT_INPUT_WIDTH 160)
    elseif(${CONFIG_MODEL_ID} EQUAL 30)
        set(MODEL_NAME mobilenet_v2_0_5_128_quant)
        set(AT_INPUT_WIDTH 128)
    elseif(${CONFIG_MODEL_ID} EQUAL 31)
        set(MODEL_NAME mobilenet_v2_0_5_96_quant)
        set(AT_INPUT_WIDTH 224)
    elseif(${CONFIG_MODEL_ID} EQUAL 32)
        set(MODEL_NAME mobilenet_v3_large_minimalistic_1_0_224_quant)
        set(AT_INPUT_WIDTH 224)
    elseif(${CONFIG_MODEL_ID} EQUAL 33)
        set(MODEL_NAME mobilenet_v3_small_1_0_224_quant)
        set(AT_INPUT_WIDTH 224)
    endif()
    set(AT_INPUT_HEIGHT ${AT_INPUT_WIDTH})
    set(AT_INPUT_COLORS 3)

    set(CONFIG_NNTOOL_MODEL_PATH models/tflite_models/${MODEL_NAME}.tflite)

    set(AT_CONSTRUCT mobilenetCNN_Construct)
    set(AT_DESTRUCT mobilenetCNN_Destruct)
    set(AT_CNN mobilenetCNN)
    set(AT_L2_MEM_ADDR mobilenet_L2_Memory)
    set(AT_L1_MEM_ADDR mobilenet_L1_Memory)
    set(AT_L3_RAM_ADDR mobilenet_L3_Memory)
    set(AT_L3_ADDR mobilenet_L3_Flash)
    set(AT_L3_2_ADDR mobilenet_L3_PrivilegedFlash)

    message(STATUS ">> Selected model: ${CONFIG_NNTOOL_MODEL_PATH} <<")
endmacro()


