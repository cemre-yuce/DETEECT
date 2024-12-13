# -*- coding: utf-8 -*-
"""
Created on Sat Nov 16 16:51:13 2024

@author: silag
"""

from ultralytics import YOLO

import torch


model=YOLO('C:/Users/silag/OneDrive/Belgeler/vscode_training/yolov8m.pt')
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
        data="C:/Users/silag/OneDrive/Masaüstü/bigdata/PCB DEFECT DETECTION ULTRA.v6i.yolov8/data.yaml",
        epochs=100,
        batch=16, 
        optimizer="Adam",
        device=device,
        imgsz=416,
        multi_scale=True,
         
        # cache=False,
        # amp=False,
        )

# # Train the YOLO model
# model = YOLO('yolov8m.pt')  # Use a smaller model if necessary (e.g., yolov8n.pt)
# model.train(data='C:/Users/silag/PCB-5/data.yaml', 
#             epochs=100, 
#             batch=8, 
#             imgsz=512, 
#             workers=2, 
#             device=0, 
#             amp=True, 
#             name="Optimized_Training")
