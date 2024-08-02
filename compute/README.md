# Compute Module

This module is responsible for sending the computed joint positions to the control module.

## Dependencies

- lcm  
Install using directions listed in lcm-proj docs
- rknn-toolkit-lite2  
Installation at [link to rknn github project](https://github.com/airockchip/rknn-toolkit2/tree/master). Enter the `rknn-toolkit-lite2/packages` directory and install the wheel that matches your python version. Ensure that you have the correct runtime installed (1.6.0), by moving the `librknnrt.so` file in the `rknpu2/runtime/librknn_api/aarch64` directory into the OrangePi5's `/usr/lib` directory.
- Adafruit BNO055  
Install using the setup file in the [old BNO055 library repository](https://github.com/adafruit/Adafruit_Python_BNO055/tree/master). (Adapting the code to use the new library is WIP)

## Running

`python3 main.py`
