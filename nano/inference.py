import ctypes
import numpy as np
import cv2
import tensorrt as trt
import pycuda.driver as cuda
import numpy as np
import json

CLASSES = (
    'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus',
    'train', 'truck', 'boat', 'traffic light', 'fire hydrant',
    'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog',
    'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 
    'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee', 
    'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat',
    'baseball glove', 'skateboard', 'surfboard', 'tennis racket',
    'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl',
    'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot',
    'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch',
    'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop',
    'mouse', 'remote', 'keyboard', 'cell phone', 'microwave',
    'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock',
    'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush'
)

#should be called after pruning
#writes the dets to json in COCO format
#note that bbox format is xywh rather than xyxy
def write_dets(dets, fname, frame_id=0):
    results = []
    for det in dets:
        b0, b1, b2, b3 = det[0:4]
        x, y = float(b0), float(b1)
        w, h = float(b2 - b0 + 1), float(b3 - b1 + 1)
        results.append({'image_id': frame_id,
                        'category_id': int(det[5]),
                        'bbox': [x, y, w, h],
                        'score': det[4] / 100})
    with open(fname, 'w') as f:
        f.write(json.dumps(results, indent=4))


def prune_dets(dets, score_thres=0.1, valid_classes=CLASSES):
    score_thres = score_thres * 100
    valid_classes = set(valid_classes) #much faster if in a set
    score_mask = dets[:, 4] >= score_thres
    labels = [CLASSES[d] for d in dets[:, 5]]
    label_mask = np.array([l in valid_classes for l in labels])
    mask = score_mask & label_mask #both must be true
    return dets[mask]

def draw_dets(img, dets, color=(255, 255, 0)):
    for det in dets:
        b0, b1, b2, b3 = det[0:4]
        score = det[4]
        label = CLASSES[det[5]]
        img = cv2.rectangle(img,
            (b0, b1),
            (b2, b3),
            color,
            thickness=1
        )
        img = cv2.putText(img,
            '%s: %s' % (label, score),
            (b0, b1 - 4),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            color,
            1
        )
    return img

def softmax(probs, axis=-1):
    probs = np.exp(probs)
    sums = np.sum(probs, axis=axis, keepdims=True)
    return probs / sums

def nms_boxes(detections, iou_threshold=0.5):
    """Apply the Non-Maximum Suppression (NMS) algorithm on the bounding
    boxes with their confidence scores and return an array with the
    indexes of the bounding boxes we want to keep.

    # Args
        detections: Nx7 numpy arrays of
                    [[x, y, w, h, box_confidence, class_id, class_prob],
                     ......]
    """
    x_coord = detections[:, 0]
    y_coord = detections[:, 1]
    width = detections[:, 2]
    height = detections[:, 3]
    box_confidences = detections[:, 4] * detections[:, 6]

    areas = width * height
    ordered = box_confidences.argsort()[::-1]

    keep = list()
    while ordered.size > 0:
        # Index of the current element:
        i = ordered[0]
        keep.append(i)
        xx1 = np.maximum(x_coord[i], x_coord[ordered[1:]])
        yy1 = np.maximum(y_coord[i], y_coord[ordered[1:]])
        xx2 = np.minimum(x_coord[i] + width[i], x_coord[ordered[1:]] + width[ordered[1:]])
        yy2 = np.minimum(y_coord[i] + height[i], y_coord[ordered[1:]] + height[ordered[1:]])

        width1 = np.maximum(0.0, xx2 - xx1 + 1)
        height1 = np.maximum(0.0, yy2 - yy1 + 1)
        intersection = width1 * height1
        union = (areas[i] + areas[ordered[1:]] - intersection)
        iou = intersection / union
        indexes = np.where(iou <= iou_threshold)[0]
        ordered = ordered[indexes + 1]

    keep = np.array(keep)
    return keep

class HostDeviceMem(object):
    """Simple helper data class that's a little nicer to use than a 2-tuple."""
    def __init__(self, host_mem, device_mem):
        self.host = host_mem
        self.device = device_mem

    def __str__(self):
        return "Host:\n" + str(self.host) + "\nDevice:\n" + str(self.device)

    def __repr__(self):
        return self.__str__()

def get_input_shape(engine):
    """Get input shape of the TensorRT YOLO engine."""
    binding = engine[0]
    assert engine.binding_is_input(binding)
    binding_dims = engine.get_binding_shape(binding)
    return binding_dims
    # if len(binding_dims) == 4:
        # return tuple(binding_dims[2:])
    # elif len(binding_dims) == 3:
        # return tuple(binding_dims[1:])
    # else:
        # raise ValueError('bad dims of binding %s: %s' % (binding, str(binding_dims)))

def allocate_buffers(engine):
    """Allocates all host/device in/out buffers required for an engine."""
    inputs = []
    outputs = []
    bindings = []
    output_idx = 0
    stream = cuda.Stream()
    for binding in engine:
        binding_dims = engine.get_binding_shape(binding)
        if len(binding_dims) == 2:
            binding_dims = (binding_dims[0], binding_dims[1], 1, 1)
        if len(binding_dims) == 4:
            # explicit batch case (TensorRT 7+)
            size = trt.volume(binding_dims)
        elif len(binding_dims) == 3:
            # implicit batch case (TensorRT 6 or older)
            size = trt.volume(binding_dims) * engine.max_batch_size
        else:
            raise ValueError('bad dims of binding %s: %s' % (binding, str(binding_dims)))
        dtype = trt.nptype(engine.get_binding_dtype(binding))
        # Allocate host and device buffers
        host_mem = cuda.pagelocked_empty(size, dtype)
        device_mem = cuda.mem_alloc(host_mem.nbytes)
        # Append the device buffer to device bindings.
        bindings.append(int(device_mem))
        # Append to the appropriate list.
        if engine.binding_is_input(binding):
            inputs.append(HostDeviceMem(host_mem, device_mem))
        else:
            # each grid has 3 anchors, each anchor generates a detection
            # output of 7 float32 values
            #assert size % 7 == 0
            outputs.append(HostDeviceMem(host_mem, device_mem))
            output_idx += 1
    assert len(inputs) == 1
    #assert len(outputs) == 1
    return inputs, outputs, bindings, stream


def do_inference_trt6(context, bindings, inputs, outputs, stream, batch_size=1):
    """do_inference (for TensorRT 6.x or lower)

    This function is generalized for multiple inputs/outputs.
    Inputs and outputs are expected to be lists of HostDeviceMem objects.
    """
    # Transfer input data to the GPU.
    [cuda.memcpy_htod_async(inp.device, inp.host, stream) for inp in inputs]
    # Run inference.
    context.execute_async(batch_size=batch_size,
                          bindings=bindings,
                          stream_handle=stream.handle)
    # Transfer predictions back from the GPU.
    [cuda.memcpy_dtoh_async(out.host, out.device, stream) for out in outputs]
    # Synchronize the stream
    stream.synchronize()
    # Return only the host outputs.
    return [out.host for out in outputs]


def do_inference(context, bindings, inputs, outputs, stream):
    """do_inference_v2 (for TensorRT 7.0+)

    This function is generalized for multiple inputs/outputs for full
    dimension networks.
    Inputs and outputs are expected to be lists of HostDeviceMem objects.
    """
    # Transfer input data to the GPU.
    [cuda.memcpy_htod_async(inp.device, inp.host, stream) for inp in inputs]
    # Run inference.
    context.execute_async_v2(bindings=bindings, stream_handle=stream.handle)
    # Transfer predictions back from the GPU.
    [cuda.memcpy_dtoh_async(out.host, out.device, stream) for out in outputs]
    # Synchronize the stream
    stream.synchronize()
    # Return only the host outputs.
    return [out.host for out in outputs]

