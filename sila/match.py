import cv2
import os

# Load the PCB image
pcb_image = cv2.imread("C:/Users/silag/OneDrive/Belgeler/type_b/on_.jpg")
output_image = pcb_image.copy()  # Create a copy for drawing

# Parameters for template matching
threshold = 0.7  # Match confidence threshold
#crop_size = 20  # Ensure this matches the template size

# Load and process each template
for filename in os.listdir("."):
    if filename.startswith("component_") and filename.endswith(".png"):
        # Load the template
        template = cv2.imread(filename, cv2.IMREAD_COLOR)
        h, w = template.shape[:2]

        # Match the template in the PCB image
        result = cv2.matchTemplate(pcb_image, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        # Draw on the output image based on match score
        if max_val >= threshold:
            # Detected: Draw a green rectangle around the match
            top_left = max_loc
            bottom_right = (top_left[0] + w, top_left[1] + h)
            cv2.rectangle(output_image, top_left, bottom_right, (0, 255, 0), 2)
            cv2.putText(output_image, filename, (top_left[0], top_left[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        else:
            # Missing: Mark with a red circle and label
            print(f"{filename} might be missing!")
            center_x = int(max_loc[0] + w / 2)
            center_y = int(max_loc[1] + h / 2)
            cv2.circle(output_image, (center_x, center_y), 15, (0, 0, 255), 2)
            cv2.putText(output_image, f"{filename} MISSING", (center_x - 20, center_y - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

# Show the output image
cv2.imshow("Detected Components", output_image)

print("Press any key to close the image and stop execution.")
cv2.waitKey(0)  # Wait indefinitely until a key is pressed
cv2.destroyAllWindows()  # Close all OpenCV windows

# Save the output image
cv2.imwrite("output_detected_components.jpg", output_image)
print("Output image saved as 'output_detected_components.jpg'")
