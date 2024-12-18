import cv2
import pandas as pd

# Load the PCB image
image = cv2.imread("C:/Users/silag/OneDrive/Belgeler/type_b/front.jpg")

# Load the manually saved component coordinates
coordinates = pd.read_csv("component_coordinates.csv")  # CSV file with X, Y

# Parameters for cropping
crop_size = 20  # Size of the cropped square around the component

# Loop through coordinates and crop small regions
for idx, row in coordinates.iterrows():
    x, y = int(row['X']), int(row['Y'])
    
    # Crop the region around each coordinate
    cropped_region = image[y-crop_size:y+crop_size, x-crop_size:x+crop_size]
    
    # Save the cropped template
    cv2.imwrite(f"component_{idx}.png", cropped_region)

print("Component templates saved successfully!")
