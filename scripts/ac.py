import cv2
from ultralytics import YOLO

# Load your trained YOLO model
model = YOLO('models/ac/best.pt')

# Class names according to your model (adjust if different)
class_names = ['AC_Off', 'AC_On']

def detect(frame, return_boxes=False):
    results = model.predict(source=frame, conf=0.2, verbose=False)
    status = 'off'
    boxes = []
    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            if class_names[cls] == 'AC_On':
                status = 'on'
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            boxes.append((x1, y1, x2, y2))
    if return_boxes:
        return status, boxes
    return status
