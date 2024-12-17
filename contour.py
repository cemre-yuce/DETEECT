import cv2
import numpy as np

# read the image
image = cv2.imread('assembly_arka.jpeg')
size = image.shape
# convert the image to grayscale format
img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# apply binary thresholding
ret, thresh = cv2.threshold(img_gray, 200, 255, cv2.THRESH_BINARY)
# visualize the binary image
# detect the contours on the binary image using cv2.ChAIN_APPROX_SIMPLE
contours1, hierarchy1 = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

# draw contours on the original image for `CHAIN_APPROX_SIMPLE`
img_black = np.zeros(size)
cv2.drawContours(img_black, contours1, -1, (255, 255, 255), 1, cv2.LINE_AA)
# see the results
cv2.imshow('Simple approximation', img_black)
cv2.imwrite("assembly_contours2.jpg", img_black)
cv2.waitKey(0)
cv2.destroyAllWindows()
