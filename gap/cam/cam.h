#ifndef __CAM_H__
#define __CAM_H__

#include "pmsis.h"
#include "bsp/camera/himax.h"

#define AT_INPUT_WIDTH    (224)
#define AT_INPUT_HEIGHT   (224)
#define AT_INPUT_COLORS (1)
#define AT_INPUT_SIZE 	(AT_INPUT_WIDTH*AT_INPUT_HEIGHT*AT_INPUT_COLORS)
#define NUM_PIXELS (AT_INPUT_WIDTH*AT_INPUT_HEIGHT)
#define CAMERA_WIDTH    (324)
#define CAMERA_HEIGHT   (244)
#define CAMERA_SIZE   	(CAMERA_HEIGHT*CAMERA_WIDTH)

//extern uint32_t v_lowbit, v_highbit;

extern struct pi_device camera;
extern pi_task_t task;
extern void captureImgSync(uint8_t* buffer);
extern void captureImgAsync(uint8_t* buffer, int use_aeg);
extern int open_camera_himax(struct pi_device *device);
extern void crop(uint8_t *img);
extern void cam_handler(void *args);
#endif
