from ultralytics import YOLO

# Load the trained model
model = YOLO("C:/Users/silag/OneDrive/Belgeler/4.Sinif/Final Project PCB/bigdata/runs/detect/train17/weights/best.pt")  # Replace with the path to your model

# Test the model on the new image
results = model.predict(source="C:/Users/silag/OneDrive/Masaüstü/final_test/buyu_see.jpg", save=True)  # Replace with the path to your image

# Print the results
print(results)
