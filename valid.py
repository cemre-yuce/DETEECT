# -*- coding: utf-8 -*-
"""
Created on Fri Dec  6 07:05:57 2024

@author: silag
"""


from ultralytics import YOLO
import torch

# Load the trained model
model = YOLO("C:/Users/silag/OneDrive/Belgeler/4.Sinif/Final Project PCB/bigdata/runs/detect/train17/weights/best.pt")  # Update path if necessary

# Check if GPU is available
if torch.cuda.is_available():
    device = torch.device("cuda:0")
    print(f"Using GPU: {torch.cuda.get_device_name(device)}")
else:
    device = torch.device("cpu")
    print("CUDA is not available. Using CPU")

# Load validation dataset
data_path = "C:/Users/silag/OneDrive/Belgeler/4.Sinif/Final Project PCB/bigdata/PCB DEFECT DETECTION ULTRA.v6i.yolov8/data.yaml"

# Run validation
if __name__ == "__main__":
    print("Starting validation...")
    try:
        model.to(device)
        results = model.val(data=data_path, device=device, verbose=True)
        print("Mean Average Precision (mAP):", results.box.map)
        print("Mean Average Precision (mAP) at IoU=0.50:", results.box.map50)
        print("Mean Average Precision (mAP) at IoU=0.75:", results.box.map75)
        print("All mAPs:", results.box.maps)
        print("Validation complete.")
    except Exception as e:
        print(f"An error occurred during validation: {e}")
