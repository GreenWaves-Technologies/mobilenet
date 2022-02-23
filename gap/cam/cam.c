#include "pmsis.h"
#include "cam.h"

struct pi_device camera = {0};
pi_task_t task = {0};
/*RT_L2_DATA uint32_t hist[256];*/
/*RT_L2_DATA uint8_t levels[256];*/

/*void equalize_histogram(uint8_t *img) {*/
    /*uint8_t pixel_val;*/
    /*uint32_t cumsum, level;*/
    /*for (int i=0; i<256; i++) {hist[i] = 0;}*/

    /*for (int i = 0; i < NUM_PIXELS; i++) {*/
        /*pixel_val = img[i];*/
        /*hist[pixel_val]++;*/
    /*}*/
    
    /*cumsum = 0;*/
    /*for (int i = 0; i < 256; i++) {*/
        /*cumsum += hist[i];*/
        /*level = (cumsum * 255) / NUM_PIXELS;*/
        /*levels[i] = (uint8_t) level;*/
    /*}*/
    
    /*for (int i = 0; i < NUM_PIXELS; i++) {*/
        /*pixel_val = img[i];*/
        /*img[i] = levels[pixel_val];*/
    /*}*/
/*}*/


void cam_handler(void *arg) {
    pi_camera_control(&camera, PI_CAMERA_CMD_STOP, 0);
}

void crop(uint8_t *img) {
    int offset = (CAMERA_WIDTH - AT_INPUT_WIDTH) / 2;
    offset = offset - 10;
    int i_start = (CAMERA_HEIGHT - AT_INPUT_HEIGHT);
    int ps = 0;
    for (int i =i_start; i < CAMERA_HEIGHT; i++) {
    	for (int j=0; j < CAMERA_WIDTH; j++) {
            if ((i  - i_start) < AT_INPUT_HEIGHT && j < AT_INPUT_WIDTH) {
            /*if (i < AT_INPUT_HEIGHT && j > 50 && j < (AT_INPUT_WIDTH + 50)) {*/
    			img[ps] = img[i * CAMERA_WIDTH + j + offset];
    			ps++;
    		}
    	}
    }
}

void captureImgAsync(uint8_t* buffer, int run_aeg) {
    if (run_aeg == 1) {
        pi_camera_control(&camera, PI_CAMERA_CMD_AEG_INIT, 0);
        rt_time_wait_us(1000000); //wait AEG init (takes ~100 ms)
    } 
    
    pi_camera_control(&camera, PI_CAMERA_CMD_STOP, 0);
    pi_task_callback(&task, cam_handler, NULL);
    pi_camera_capture_async(&camera, buffer, CAMERA_WIDTH * CAMERA_HEIGHT, &task);
    pi_camera_control(&camera, PI_CAMERA_CMD_START, 0);
    pi_task_wait_on(&task);
    crop(buffer);
    /*equalize_histogram(Input_1);*/
}


void captureImgSync(uint8_t* buffer) {
    pi_camera_control(&camera, PI_CAMERA_CMD_START, 0);
    pi_camera_capture(&camera, buffer, (uint32_t) CAMERA_SIZE);
    pi_camera_control(&camera, PI_CAMERA_CMD_STOP, 0);
    crop(buffer);
    /*equalize_histogram(Input_1);*/
}


/*int openCamera(struct pi_device *device) {*/
int openCamera() {
    /*struct pi_device* device = &camera;*/
    struct pi_himax_conf cam_conf;
    pi_himax_conf_init(&cam_conf);
    pi_open_from_conf(&camera, &cam_conf);
    if (pi_camera_open(&camera)) {
        return -1;
    }
    pi_camera_control(&camera, PI_CAMERA_CMD_AEG_INIT, 0);
    rt_time_wait_us(1000000); //wait AEG init (takes ~100 ms)
    return 0;
}

