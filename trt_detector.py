import ctypes
import numpy as np
import cv2
import tensorrt as trt
import pycuda.driver as cuda
from utils.inference import HostDeviceMem, get_input_shape, allocate_buffers, do_inference, nms_boxes
import time

class TRTDetector(object):
    def _load_engine(self):
        with open(self.model, 'rb') as f, trt.Runtime(self.trt_logger) as runtime:
            return runtime.deserialize_cuda_engine(f.read())

    def __init__(self, model, category_num=80, letter_box=False, cuda_ctx=None):
        """Initialize TensorRT plugins, engine and conetxt."""
        self.model = model
        self.category_num = category_num
        self.letter_box = letter_box
        self.cuda_ctx = cuda_ctx
        if self.cuda_ctx:
            self.cuda_ctx.push()
        self.inference_fn = do_inference #if trt.__version__[0] < '7' else do_inference_v2
        self.trt_logger = trt.Logger(trt.Logger.INFO)
        self.engine = self._load_engine()
        self.input_shape = get_input_shape(self.engine)
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

    def preprocess(self, img, input_shape, letter_box=False):
        if letter_box:
            img_h, img_w, _ = img.shape
            new_h, new_w = input_shape[0], input_shape[1]
            offset_h, offset_w = 0, 0
            if (new_w / img_w) <= (new_h / img_h):
                new_h = int(img_h * new_w / img_w)
                offset_h = (input_shape[0] - new_h) // 2
            else:
                new_w = int(img_w * new_h / img_h)
                offset_w = (input_shape[1] - new_w) // 2
            resized = cv2.resize(img, (new_w, new_h))
            img = np.full((input_shape[0], input_shape[1], 3), 127, dtype=np.uint8) 
            img[offset_h:(offset_h + new_h), offset_w:(offset_w + new_w), :] = resized
        else:
            img = cv2.resize(img, (input_shape[1], input_shape[0]))

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype(np.float32)
        mean = np.array([123.675, 116.28, 103.53]).astype(np.float32)
        std = np.array([58.395, 57.12, 57.375]).astype(np.float32)
        mean = np.expand_dims(mean, axis=(0, 1))
        std = np.expand_dims(std, axis=(0, 1))
        img = (img - mean) / std
        img = img.transpose((2, 0, 1))
        img = np.expand_dims(img, axis=0)
        return img
        
    #[[x, y, w, h, box_confidence, class_id, class_prob],

    def postprocess(self, outputs, img_w, img_h, input_shape, letter_box=False):
        scale_x = img_w / input_shape[1]
        scale_y = img_h / input_shape[0]
        
        detections = outputs[0].reshape(1, -1, 7)[0] 
        x1, y1, x2, y2 = np.split(detections[:, 0:4], 4, axis=-1)
        #x, y, w, h = (x1 + x2)/2, (y1 + y2)/2, (x2 - x1), (y2 - y1)
        x, y, w, h = x1, y1, x2 - x1 + 1, y2 - y1 + 1
        x, w = x * scale_x, w * scale_x
        y, h = y * scale_y, h * scale_y
        detections[:, 0:4] = np.concatenate([x,y,w,h], axis=-1)
        
        #conf_scores = class_scores[..., -1][:, np.newaxis] 
        #class_scores = class_scores[..., 0:80]
        
        #class_idx = np.argmax(class_scores, axis=-1)[:, np.newaxis] 
        #class_prob = np.amax(class_scores, axis=-1)[:, np.newaxis] 

        #detections = np.concatenate([pred_bbox, conf_scores, class_idx, class_prob], axis=-1)
        detections  = detections[detections[:, 4] * detections[:, 6] >= 1e-2]
        scores = detections[:, 4] * detections[:, 6]
        classes = detections[:, 5]

        nms_detections = np.zeros((0, 7), dtype=detections.dtype)
        for class_id in set(detections[:, 5]):
            idxs = np.where(detections[:, 5] == class_id)
            cls_detections = detections[idxs]
            keep = nms_boxes(cls_detections, 0.5)
            nms_detections = np.concatenate([nms_detections, cls_detections[keep]], axis=0)
        xx = nms_detections[:, 0].reshape(-1, 1)
        yy = nms_detections[:, 1].reshape(-1, 1)
        #if letter_box:
        #    xx = xx - offset_w
        #    yy = yy - offset_h
        ww = nms_detections[:, 2].reshape(-1, 1)
        hh = nms_detections[:, 3].reshape(-1, 1)
        boxes = np.concatenate([xx, yy, xx+ww, yy+hh], axis=1) + 0.5
        boxes = boxes.astype(np.int)
        scores = nms_detections[:, 4] * nms_detections[:, 6]
        classes = nms_detections[:, 5]
        
        # clip x1, y1, x2, y2 within original image
        boxes[:, [0, 2]] = np.clip(boxes[:, [0, 2]], 0, img_w-1)
        boxes[:, [1, 3]] = np.clip(boxes[:, [1, 3]], 0, img_h-1)
        
        # if self.cuda_ctx:
            # self.cuda_ctx.pop()

        return boxes, scores, classes
        
        
    def detect(self, img, letter_box=None):
        """Detect objects in the input image."""
        timing = {}
        
        start = time.time()
        letter_box = self.letter_box if letter_box is None else letter_box
        img_resized = self.preprocess(img, self.input_shape, letter_box)
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
        boxes, scores, classes = self.postprocess(
            outputs, img.shape[1], img.shape[0], 
            input_shape=self.input_shape,
            letter_box=letter_box
        )
        timing['postprocess'] = time.time() - start
        self.timings.append(timing)
        return boxes, scores, classes
