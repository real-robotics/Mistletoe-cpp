import numpy as np
import platform
from rknnlite.api import RKNNLite
import time
import os 
import random


file_path = os.path.abspath(__file__)
directory_path = os.path.dirname(file_path)
# Define the path to your RKNN model
rknn_model = directory_path + '/rknn_models/ppo_policy.rknn'

# Initialize RKNNLite instance
rknn_lite = RKNNLite()

# Load the RKNN model
ret = rknn_lite.load_rknn(rknn_model)
if ret != 0:
    print(f"Failed to load RKNN model. Error code: {ret}")
    exit(ret)

# Initialize runtime with NPU_CORE_0
ret = rknn_lite.init_runtime(core_mask=RKNNLite.NPU_CORE_0)
if ret != 0:
    print(f"Failed to initialize runtime. Error code: {ret}")
    exit(ret)

# Main loop for inference with dynamically changing input
# while True:
# Generate new random input data for each inference
test_input = np.array([[ 0.9186, -0.3394,  0.0429, -0.9095, -0.2321, -0.3704, -0.0206, -0.0076,
         -0.9710,  0.8288, -0.3658, -0.6293,  0.1615,  0.0612, -0.0264,  0.2070,
          0.0523,  0.4267,  0.3397, -0.0393,  0.6484, -0.5240, -0.4888,  0.6329,
         -2.7514, -2.8664, -0.7820,  0.6780,  2.3711,  1.3693, -4.5794, -6.0255,
          0.1859,  0.9205, -2.4844, -2.0339, -0.7092, -1.1932, -0.6209,  1.3135,
          1.4991,  2.4324, -0.3357, -2.2901, -0.8300, -0.9989, -1.8241, -2.0658]]).astype(np.float32)
print(test_input)

# Perform inference timing
start_time = time.time()
outputs = rknn_lite.inference(inputs=test_input)
print(outputs)
end_time = time.time()
inference_time = end_time - start_time

# Print inference time and outputs
print(f'Inference time: {inference_time:.6f} seconds')
# Optionally add a delay or trigger condition for looping
# time.sleep(0.01)