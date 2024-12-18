import cv2
import numpy as np
from os import listdir
from os.path import isfile, join

mypath = "C:/Users/talha/PycharmProjects/PCB_defect/templates2"
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

drag = False
drag_start = (0, 0)
drag_end = (0, 0)
patterns = []
regions = []
show_regions = False
show_mask = True
scale_factor = 1.0  # Global scale factor for resizing


def on_mouse(event, x, y, flags, params):
    global drag, drag_start, drag_end, img, patterns, regions, scale_factor

    # Scale mouse coordinates back to original image size
    scaled_x = int(x / scale_factor)
    scaled_y = int(y / scale_factor)

    if event == cv2.EVENT_LBUTTONDOWN:
        # Use scaled coordinates for cropping and saving
        drag_start = (scaled_x, scaled_y)
        drag_end = (scaled_x, scaled_y)
        drag = True

    elif event == cv2.EVENT_LBUTTONUP:
        drag = False
        drag_end = (scaled_x, scaled_y)
        if (drag_end[1] - drag_start[1]) > 10 and (drag_end[0] - drag_start[0]) > 10:
            crop = img[drag_start[1]:drag_end[1], drag_start[0]:drag_end[0]]
            name = f"{drag_start[0]}-{drag_start[1]}.jpg"
            cv2.imwrite(join(mypath, name), crop)
            pattern = cv2.imread(join(mypath, name), 1)
            patterns.append(pattern)  # Keep patterns in BGR format
            rectparts = [drag_start[0], drag_start[1], pattern.shape[1], pattern.shape[0]]
            regions.append(rectparts)
            drag_start = (0, 0)
            drag_end = (0, 0)

    elif event == cv2.EVENT_MOUSEMOVE and drag:
        # Update only for the drag rectangle
        drag_end = (scaled_x, scaled_y)


def process_image(image_path):
    global drag_start, drag_end, img, patterns, regions, show_regions, show_mask, scale_factor

    # Load the input image
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not load image file {image_path}")
        return

    # Load the mask
    white_image = np.ones([1920, 1080])
    mask = white_image
    if mask is None:
        print("Error: mask not found.")
        return

    # Resize the image if it's too large for the screen
    screen_width = 1280  # Example screen width
    screen_height = 960  # Example screen height
    frame_height, frame_width = img.shape[:2]
    scale_factor = min(screen_width / frame_width, screen_height / frame_height, 1.0)
    resized_img = cv2.resize(img, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_AREA)

    # Resize the mask to match the image dimensions
    if mask.shape[:2] != img.shape[:2]:
        mask = cv2.resize(mask, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_NEAREST)

    # Ensure the mask is single-channel 8-bit
    if len(mask.shape) > 2:
        mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
    if mask.dtype != np.uint8:
        mask = cv2.convertScaleAbs(mask)

    # Load template patterns and regions
    for i in onlyfiles:
        pattern = cv2.imread(join(mypath, i), 1)
        patterns.append(pattern)  # Keep patterns in BGR format
        rectparts = [int(x) for x in i.split('.')[0].split('-')]
        rectparts.extend([pattern.shape[1], pattern.shape[0]])
        regions.append(rectparts)

    # Set up the display window and mouse callback
    cv2.namedWindow('detEEct AOI')
    cv2.setMouseCallback('detEEct AOI', on_mouse, 0)

    try:
        while True:
            diff = resized_img.copy()

            if show_mask:
                resized_mask = cv2.resize(mask, (resized_img.shape[1], resized_img.shape[0]),
                                          interpolation=cv2.INTER_NEAREST)
                diff = cv2.bitwise_and(diff, diff, mask=resized_mask)

            # Draw the rectangle during dragging
            if drag and drag_start != (0, 0) and drag_end != (0, 0):
                # Scale the drag rectangle for display
                scaled_drag_start = (int(drag_start[0] * scale_factor), int(drag_start[1] * scale_factor))
                scaled_drag_end = (int(drag_end[0] * scale_factor), int(drag_end[1] * scale_factor))
                cv2.rectangle(diff, scaled_drag_start, scaled_drag_end, (255, 0, 0), 1)

            for i, pattern in enumerate(patterns):
                x1, y1 = regions[i][:2]
                w, h = regions[i][2:]
                x2, y2 = x1 + w, y1 + h

                if show_regions:
                    # Scale coordinates for visual feedback
                    scaled_x1 = int(x1 * scale_factor)
                    scaled_y1 = int(y1 * scale_factor)
                    scaled_x2 = int(x2 * scale_factor)
                    scaled_y2 = int(y2 * scale_factor)

                    cv2.rectangle(diff, (scaled_x1, scaled_y1), (scaled_x2, scaled_y2), (0, 255, 0), 1)

                # Adjust ROI to ensure it's within bounds
                sub_y1 = max(0, y1 - 10)
                sub_y2 = min(img.shape[0], y2 + 10)
                sub_x1 = max(0, x1 - 10)
                sub_x2 = min(img.shape[1], x2 + 10)

                sub = img[sub_y1:sub_y2, sub_x1:sub_x2]

                # Check if the ROI (`sub`) is larger than the `pattern`
                if sub.shape[0] >= pattern.shape[0] and sub.shape[1] >= pattern.shape[1]:
                    res = cv2.matchTemplate(sub, pattern, cv2.TM_CCOEFF_NORMED)
                    threshold = 0.80
                    loc = np.where(res >= threshold)

                    for pt in zip(*loc[::-1]):
                        scaled_pt_x = int((pt[0] + sub_x1) * scale_factor)
                        scaled_pt_y = int((pt[1] + sub_y1) * scale_factor)
                        scaled_pt_x2 = int((pt[0] + sub_x1 + w) * scale_factor)
                        scaled_pt_y2 = int((pt[1] + sub_y1 + h) * scale_factor)

                        cv2.rectangle(diff, (scaled_pt_x, scaled_pt_y),
                                      (scaled_pt_x2, scaled_pt_y2), (0, 0, 0), -1)
                else:
                    # Log a warning or handle cases where the subregion is smaller
                    print(f"Warning: Subregion smaller than pattern for region {i}. Skipping template matching.")

            cv2.imshow('detEEct AOI', diff)

            # Handle user input
            char = chr(cv2.waitKey(1) & 255)
            if char == 'q' or char == chr(27):  # Quit on 'q' or Esc
                break
            elif char == 'd':
                show_regions = not show_regions
            elif char == 's':
                show_mask = not show_mask

    finally:
        cv2.destroyAllWindows()


def main():
    image_path = "C:/Users/talha/PycharmProjects/PCB_defect/buyutech_arka_zoomed_defected.jpg"
    process_image(image_path)


if __name__ == '__main__':
    main()
