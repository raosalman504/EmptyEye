from ultralytics import YOLO
import cv2

# Load COCO-pretrained YOLO model
model = YOLO('yolo11n.pt')  # or 'yolov8s.pt' for better accuracy

# --- Refactored for integration ---
def detect(frame, return_boxes=False):
    results = model.predict(source=frame, conf=0.3, verbose=False)
    found = False
    boxes = []
    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            if cls == 67:  # Class ID for 'cell phone'
                found = True
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                boxes.append((x1, y1, x2, y2))
    if return_boxes:
        return found, boxes
    return found
