import cv2
import numpy as np
import platform
from rknnlite.api import RKNNLite
import time

class VelocityTrackingModel:
    def __init__(self, model_path):
        # Initialize RKNNLite instance
        self.rknn_lite = RKNNLite()
        ret = self.rknn_lite.load_rknn(model_path)
        ret = self.rknn_lite.init_runtime(core_mask=RKNNLite.NPU_CORE_0)

        # Load the RKNN model
        if ret != 0:
            print(f"Failed to load RKNN model. Error code: {ret}")
            exit(ret)

    def compute_inference(self, observation_dict):
        start_time = time.time()
        outputs = self.rknn_lite.inference(inputs=observation_dict)
        return outputs
