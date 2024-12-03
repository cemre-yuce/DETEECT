# -*- coding: utf-8 -*-
"""
Created on Sat Nov 16 14:12:33 2024

@author: buses
"""

from ultralytics import YOLO

import torch


model=YOLO("C:/Users/buses/Desktop/PCB/datasets/yolov8m.pt")
### load a model
#model=YOLO("yolov8m.pt")
# print("Starting trainin ...")
if torch.cuda.is_available():
    device=torch.device("cuda:0")
    print(f"Using GPU: {torch.cuda.get_device_name(device)}")
else:
    device=torch.device("cpu")
    print("CUDA is not available. Using CPU")

### train the model
#results=model.train(data="config.yaml", epochs=20)



device=torch.device("cuda")
if __name__ == "__main__":
    model.to(device)
    model.train(
        data="C:/Users/buses/Desktop/PCB/datasets/data.yaml",
        epochs=100,
        batch=16, 
        optimizer="Adam",
        lr0=1e-5,
        device=device,
        imgsz=640,
         
        # cache=False,
        # amp=False,
        ) 