# Compute Module

This module is responsible for sending the computed joint positions to the control module. The module should be run on a OrangePi5 with [the official Ubuntu Image](http://www.orangepi.org/html/hardWare/computerAndMicrocontrollers/service-and-support/Orange-pi-5.html).

## Dependencies
- python 3.10
- lcm  
Install using directions listed in lcm-proj docs
- rknn-toolkit-lite2  
Installation at [link to rknn github project](https://github.com/airockchip/rknn-toolkit2/tree/master). Enter the `rknn-toolkit-lite2/packages` directory and install the wheel that matches your python version. Ensure that you have the correct runtime installed (1.6.0), by moving the `librknnrt.so` file in the `rknpu2/runtime/librknn_api/aarch64` directory into the OrangePi5's `/usr/lib` directory.
- Adafruit BNO055  
Install using the setup file in the [old BNO055 library repository](https://github.com/adafruit/Adafruit_Python_BNO055/tree/master). (Adapting the code to use the new library is WIP)

## Before Running  
Ensure that you have enabled and configured i2c on the OrangePi5, as described in the manual of the Orangepi5. The code assumes you have connected the BNO055 on the i2c bus 1. After enabling wifi after connecting the wifi-module (should be bought seperately), run the steps outlined in `orangepi-setup.md` to ensure that your system is configured properly to route the LCM traffic, and is setup as a wireless hotspot.

## Running

`python3 main.py`  
If you have properly configured your setup, you should be able to connect to the mistletoe wifi network via your desktop, and get feedback using the dashboard. Steps on setting up the dashboard are in the `/dashboard/main-dashboard` directory.
