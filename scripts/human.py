from ultralytics import YOLO
import cv2

# Load pre-trained YOLOv8 model (trained on COCO, includes 'person')
model = YOLO('yolo11n.pt')  # or your human detection model

def detect(frame, return_boxes=False):
    results = model(frame)
    found = False
    boxes = []
    for result in results:
        for box in result.boxes:
            cls = int(box.cls[0])
            if cls == 0:  # class 0 is 'person' in COCO
                found = True
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                boxes.append((x1, y1, x2, y2))
    if return_boxes:
        return found, boxes
    return found
