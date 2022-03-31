import cv2
import time
import torch
import numpy as np

from utils.datasets import letterbox
from models.experimental import attempt_load
from utils.torch_utils import select_device
from utils.general import check_img_size, non_max_suppression, \
    scale_coords, set_logging


class YoloV5Model(object):

    def __init__(self):
        set_logging()
        self._model_path = './self_driving_yolov5.pt'
        self._device = select_device('')
        self._half = self._device.type != 'cpu'
        self._model = attempt_load(self._model_path, map_location=self._device)

        if self._half:
            self._model.half()  # to FP16

        self._classes = self._model.module.names if hasattr(
            self._model, 'module') else self._model.names

        self._stride = int(self._model.stride.max())
        self._conf_threshold = 0.25
        self._iou_threshold = 0.45
        self._agnostic_nms = False

    def main(self, request):
        image_bytes = request.get_data()
        img0 = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), -1)
        image_size = check_img_size(416, s=self._stride)

        if self._device.type != 'cpu':
            self._model(torch.zeros(1, 3, image_size, image_size).to(self._device).type_as(
                next(self._model.parameters())))

        img = self._preprocess(img0, image_size)
        detected_objects = self._inference(img, img0, image_size)
        return detected_objects

    def _preprocess(self, image, image_size):
        img = letterbox(image, image_size, stride=self._stride)[0]
        img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
        img = np.ascontiguousarray(img)
        img = torch.from_numpy(img).to(self._device)
        img = img.half() if self._half else img.float()  # uint8 to fp16/32
        img /= 255.0  # 0 - 255 to 0.0 - 1.0
        if img.ndimension() == 3:
            img = img.unsqueeze(0)
        return img

    def _inference(self, img, img0, image_size):
        t0 = time.time()
        pred = self._model(img, augment=False)[0]

        pred = non_max_suppression(pred, self._conf_threshold,
                                   self._iou_threshold, classes=None, agnostic=self._agnostic_nms)

        detected_objects = []
        for i, det in enumerate(pred):
            if len(det):
                det[:, :4] = scale_coords(
                    img.shape[2:], det[:, :4], img0.shape).round()
 
                for *xyxy, conf, cls in reversed(det):
                    x1 = int(xyxy[0])
                    y1 = int(xyxy[1])
                    x2 = int(xyxy[2])
                    y2 = int(xyxy[3])

                    width = (x2 - x1) / image_size
                    height = (y2 - y1) / image_size
                    left = x1 / image_size
                    top = y1 / image_size

                    detection = {
                        "type": "entity",
                        "entity": {
                            "tag": {
                                "value": self._classes[int(cls)],
                                "confidence": f"{conf:.2f}"
                            },
                            "box": {
                                "l": left,
                                "t": top,
                                "w": width,
                                "h": height
                            }
                        }
                    }
                    detected_objects.append(detection)
        print(f'Done. ({time.time() - t0:.3f}s)')
        return detected_objects
