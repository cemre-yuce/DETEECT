import cv2
import numpy as np

# Load an image

img = cv2.imread("buyutech_arka.jpeg")

# Convert the image to grayscale


gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# Perform Canny edge detection
# Find contours in the edges image


contours, hierarchy = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Iterate over each contour


for contour in contours:

    # Approximate the contour to a polygon

    polygon = cv2.approxPolyDP(contour, 0.1 * cv2.arcLength(contour, True), True)

    # Check if the polygon has 4 sides

    if len(polygon) == 4:
        # Draw the rectangle on the image

        x, y, w, h = cv2.boundingRect(polygon)

        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Show the result

cv2.imshow("Result", img)

cv2.waitKey(0)

cv2.destroyAllWindows()
