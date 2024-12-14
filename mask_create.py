import cv2
import numpy as np

img = cv2.imread('assemblyedges.jpg')
size = img.shape
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
ret, thresh = cv2.threshold(gray, 220, 255, 0)
img_black = np.zeros(size)
contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
for contour in contours:

    # Approximate the contour to a polygon

    polygon = cv2.approxPolyDP(contour, 0.1 * cv2.arcLength(contour, True), True)

    # Check if the polygon has 4 sides

    if (len(polygon) == 4) and (1002000>cv2.contourArea(polygon)> 90 ):
        # Draw the rectangle on the image

        x, y, w, h = cv2.boundingRect(polygon)

        cv2.rectangle(img_black, (x, y), (x + w, y + h), (255, 255, 255), cv2.FILLED)

#cv2.drawContours(img_black, contours, -1, (255, 255, 255), 1)

img_black_resized = cv2.resize(img_black, (1920, 1080))
cv2.imwrite("pcb_contours5.jpeg", img_black_resized)
cv2.imshow('Simple approximation', img_black_resized)
cv2.waitKey(0)
