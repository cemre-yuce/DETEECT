import cv2
import pandas as pd

# Load the image
image_path = "C:/Users/silag/OneDrive/Belgeler/type_b/front.jpg"
image = cv2.imread(image_path)
if image is None:
    print(f"Error: Unable to load image at {image_path}")
    exit()

# List to store component data
component_data = []

# Mouse callback function to capture clicks
def capture_click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:  # Left-click to record position
        print(f"Component clicked at: ({x}, {y})")
        component_data.append((x, y))  # Append coordinates to list
        # Draw a small circle at the clicked point for visual feedback
        cv2.circle(image, (x, y), 5, (0, 0, 255), -1)
        cv2.imshow("Click Components", image)

# Set up window and mouse callback
cv2.namedWindow("Click Components")
cv2.setMouseCallback("Click Components", capture_click)

print("Click on the components. Press 'q' to quit and save data.")
cv2.imshow("Click Components", image)

# Event loop
while True:
    key = cv2.waitKey(1)
    if key == ord('q'):  # Quit the program when 'q' is pressed
        break

# Save coordinates to a CSV file
df = pd.DataFrame(component_data, columns=["X", "Y"])
output_path = "component_coordinates.csv"
df.to_csv(output_path, index=False)
print(f"Component coordinates saved to {output_path}")

cv2.destroyAllWindows()
