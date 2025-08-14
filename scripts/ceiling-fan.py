#vertix
#surronding

import cv2
from ultralytics import YOLO

# Load the trained model
model = YOLO('models/ceiling_fan/weights/best.pt')  # Change path if needed

# Class labels from your training
class_names = ['off', 'on']

# Colors: red for 'off', green for 'on'
box_colors = {
    'off': (0, 0, 255),
    'on': (0, 255, 0)
}

# --- Refactored for integration ---
def detect(frame, return_boxes=False):
    results = model.predict(source=frame, conf=0.2, verbose=False)
    status = 'off'
    boxes = []
    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            if class_names[cls] == 'on':
                status = 'on'
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            boxes.append((x1, y1, x2, y2))
    if return_boxes:
        return status, boxes
    return status
