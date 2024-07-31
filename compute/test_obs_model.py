import numpy as np
import platform
from rknnlite.api import RKNNLite
import time
import os 
import random
file_path = os.path.abspath(__file__)
directory_path = os.path.dirname(file_path)
# Define the path to your RKNN model
rknn_model = directory_path + '/rknn_models/state_estimator.rknn'

# Function to generate random input data
def generate_random_input(batch_size, input_size):
    return np.random.rand(batch_size, input_size).astype(np.float32)

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
test_input = np.array([random.random() * 5 for _ in range(45)]).astype(np.float32)
print(test_input)
test_input_real = generate_random_input(1, 45)
print(test_input_real)

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