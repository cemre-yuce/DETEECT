# -*- coding: utf-8 -*-
"""
Created on Tue Jul 16 08:12:59 2024

@author: buse
"""

from ultralytics import YOLO
import os


# from ultralytics.utils.plotting import Annotator
# class CustomAnnotator(Annotator):
#     def __init__(self, *args, text_size=0.1, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.text_size=text_size
#     def box_label(self, *args, **kwargs):
#         kwargs["font_scale"]=self.text_size
#         return super().box_label(*args, **kwargs)



train_number=16
model=YOLO(f"C:/Users/buses/Desktop/PCB/datasets/runs/detect/train{train_number}/weights/best.pt")

test_img_path="C:/Users/buses/Desktop/PCB/datasets/test/images"
pred_path=f"C:/Users/buses/Desktop/PCB/datasets/test/pred_results_train{train_number}"
os.makedirs(pred_path, exist_ok=True)

results=model.predict(
    source=test_img_path,
    save=True,
    save_txt=True,
    save_dir=pred_path,
    name=f"pred_train{train_number}",
    line_width=1)



