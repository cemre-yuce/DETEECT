import os
from pdf2image import convert_from_path
import cv2
import numpy as np

# Set your PDF filename here
pdf_filename = 'Component_placement.PDF'  # Replace with your PDF file name

# Get the PDF name (without extension)
pdf_name = os.path.splitext(pdf_filename)[0]

# Convert PDF pages to images
pages = convert_from_path(pdf_filename, 600)

# Process and save each page (image) without any changes
for page_number, page in enumerate(pages):
    # Convert PIL Image to NumPy array (for OpenCV)
    image = np.array(page)

    # Save the image as PNG or JPG without any modifications
    output_filename = f"{pdf_name}.page{page_number + 1}.png"  # Change .png to .jpg if you prefer
    cv2.imwrite(output_filename, image)  # Save the image as it is (no modifications)

    # Optionally, display the image (this is optional)
    cv2.imshow(f'Page {page_number + 1}', image)
    cv2.waitKey(0)  # Wait for a key press

cv2.destroyAllWindows()
