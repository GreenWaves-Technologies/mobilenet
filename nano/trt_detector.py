import ctypes
import numpy as np
import tensorrt as trt
import pycuda.autoinit  # This is needed for initializing CUDA driver
import pycuda.driver as cuda
from inference import HostDeviceMem, get_input_shape, allocate_buffers, do_inference, nms_boxes, prune_dets
import time

class TRTDetector(object):
    def _load_engine(self):
        with open(self.model, 'rb') as f, trt.Runtime(self.trt_logger) as runtime:
            return runtime.deserialize_cuda_engine(f.read())

    def __init__(self, model, category_num=80, num_dets=50, cuda_ctx=None):
        """Initialize TensorRT plugins, engine and conetxt."""
        self.model = model
        self.category_num = category_num
        self.cuda_ctx = cuda_ctx
        if self.cuda_ctx:
            self.cuda_ctx.push()
        self.inference_fn = do_inference
        self.trt_logger = trt.Logger(trt.Logger.INFO)
        self.engine = self._load_engine()
        self.input_shape = get_input_shape(self.engine)
        self.num_dets = num_dets
        self.timings = []

        try:
            self.context = self.engine.create_execution_context()
            self.inputs, self.outputs, self.bindings, self.stream = allocate_buffers(self.engine)
        except Exception as e:
            raise RuntimeError('fail to allocate CUDA resources') from e
        finally:
            if self.cuda_ctx:
                self.cuda_ctx.pop()

    def __del__(self):
        """Free CUDA memories."""
        del self.outputs
        del self.inputs
        del self.stream

    def preprocess(self, img, input_shape):
        return img
        # img = cv2.resize(img, (input_shape[1], input_shape[0]))
        # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype(np.float32)
        # mean = np.array([123.675, 116.28, 103.53]).astype(np.float32)
        # std = np.array([58.395, 57.12, 57.375]).astype(np.float32)
        # mean = np.expand_dims(mean, axis=(0, 1))
        # std = np.expand_dims(std, axis=(0, 1))
        # img = (img - mean) / std
        # img = img.transpose((2, 0, 1))
        # img = np.expand_dims(img, axis=0)
        # return img
        
    #[[x, y, w, h, box_confidence, class_id, class_prob],

    def postprocess(self, outputs, img_w, img_h, input_shape):
        img_w, img_h = 224, 224
        # scale_x = img_w / input_shape[1]
        # scale_y = img_h / input_shape[0]
        scale_x, scale_y = 1, 1
        
        dets = outputs[0].reshape(1, -1, 7)[0] 
        x1, y1, x2, y2 = np.split(dets[:, 0:4], 4, axis=-1)
        #x, y, w, h = (x1 + x2)/2, (y1 + y2)/2, (x2 - x1), (y2 - y1)
        x, y, w, h = x1, y1, x2 - x1 + 1, y2 - y1 + 1
        x, w = x * scale_x, w * scale_x
        y, h = y * scale_y, h * scale_y
        dets[:, 0:4] = np.concatenate([x,y,w,h], axis=-1)
        
        #conf_scores = class_scores[..., -1][:, np.newaxis] 
        #class_scores = class_scores[..., 0:80]
        
        #class_idx = np.argmax(class_scores, axis=-1)[:, np.newaxis] 
        #class_prob = np.amax(class_scores, axis=-1)[:, np.newaxis] 

        #dets = np.concatenate([pred_bbox, conf_scores, class_idx, class_prob], axis=-1)
        dets  = dets[dets[:, 4] * dets[:, 6] >= 1e-2]
        scores = dets[:, 4] * dets[:, 6]
        classes = dets[:, 5]

        nms_dets = np.zeros((0, 7), dtype=dets.dtype)
        for class_id in set(dets[:, 5]):
            idxs = np.where(dets[:, 5] == class_id)
            cls_dets = dets[idxs]
            keep = nms_boxes(cls_dets, 0.5)
            nms_dets = np.concatenate([nms_dets, cls_dets[keep]], axis=0)
        xx = nms_dets[:, 0].reshape(-1, 1)
        yy = nms_dets[:, 1].reshape(-1, 1)
        ww = nms_dets[:, 2].reshape(-1, 1)
        hh = nms_dets[:, 3].reshape(-1, 1)
        boxes = np.concatenate([xx, yy, xx+ww, yy+hh], axis=1) + 0.5
        scores = nms_dets[:, 4] * nms_dets[:, 6]
        classes = nms_dets[:, 5]
        
        # clip x1, y1, x2, y2 within original image
        boxes[:, [0, 2]] = np.clip(boxes[:, [0, 2]], 4, img_w-4)
        boxes[:, [1, 3]] = np.clip(boxes[:, [1, 3]], 16, img_h-4)

        dets = np.concatenate((
            boxes, 
            scores[:, np.newaxis] * 100, #[0,1] -> [0,100]
            classes[:, np.newaxis]), 
        axis=1)

        dets = dets.astype(np.uint16)
        # dets = prune_dets(dets, valid_classes=('laptop',))
        dets = prune_dets(dets)
        # if len(dets) > self.num_dets:

        # idx = np.argsort(-dets[:, -2]) #sort by score
        # dets = dets[idx]
        # dets = dets[0:self.num_dets]
        # zeros = np.zeros((self.num_dets - len(dets), 6), dtype=dets.dtype)
        # dets = np.concatenate((dets, zeros), axis=0)
        
        # if self.cuda_ctx:
            # self.cuda_ctx.pop()

        return dets
        
        
    def detect(self, img):
        """Detect objects in the input image."""
        timing = {}
        
        start = time.time()
        img_resized = self.preprocess(img, self.input_shape)
        self.inputs[0].host = np.ascontiguousarray(img_resized)
        if self.cuda_ctx:
            self.cuda_ctx.push()
        timing['preprocess'] = time.time() - start
        
        start = time.time()
        outputs = self.inference_fn(
            context=self.context,
            bindings=self.bindings,
            inputs=self.inputs,
            outputs=self.outputs,
            stream=self.stream
        )
        if self.cuda_ctx:
            self.cuda_ctx.pop()
        timing['model'] = time.time() - start

        start = time.time()
        detections = self.postprocess(
            outputs, img.shape[1], img.shape[0], 
            input_shape=self.input_shape
        )
        timing['postprocess'] = time.time() - start
        self.timings.append(timing)
        return detections
