import cv2
import numpy as np

cv2.destroyAllWindows()

threshold = 150

cv2.namedWindow('before', cv2.WINDOW_KEEPRATIO)
cv2.namedWindow('after', cv2.WINDOW_KEEPRATIO)

image_name = 'buyutech_on_20cm_whitebalanced.jpg'
imageCropped_name = 'buyutech_on_20cm_whitebalanced_cropped.jpg'

# Read the image
image = cv2.imread(image_name)

# Convert to grayscale for segmentation
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Binary threshold
(T, thresh) = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY_INV)

# Find contours
contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

# Find the largest contour
areas = [cv2.contourArea(c) for c in contours]
max_idx = np.argmax(areas)
cnt = contours[max_idx]

# Get the bounding rectangle of the largest contour
x, y, w, h = cv2.boundingRect(cnt)

# Draw the bounding rectangle (optional)
cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)

# Crop the PCB using the bounding rectangle
cropped = image[y:y + h, x:x + w]

# Display results
cv2.imshow('before', image)
cv2.imshow('after', cropped)

# Save the cropped image
cv2.imwrite(imageCropped_name, cropped)

cv2.waitKey(0)
cv2.destroyAllWindows()
