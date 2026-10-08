import os, json, cv2
from ultralytics import YOLO
MODEL_PATH = 'runs/detect/runs/train/sketch_yolo/weights/best.pt'
INPUT_IMAGE = 'dataset/custom_sketches/img1.jpeg'
OUTPUT_DIR = 'pipeline_output'
CROPS_DIR = os.path.join(OUTPUT_DIR, 'crops')
os.makedirs(CROPS_DIR, exist_ok=True)
print(f'Loading model from {MODEL_PATH}...')
model = YOLO(MODEL_PATH)
image = cv2.imread(INPUT_IMAGE)
if image is None:
    raise FileNotFoundError(f'Image not found: {INPUT_IMAGE}')
h, w, _ = image.shape
results = model.predict(source=image, conf=0.45, iou=0.5, verbose=False)[0]
detected_items = []
print(f'Total components detected: {len(results.boxes)}')
for idx, box in enumerate(results.boxes):
    cls_id = int(box.cls[0].item())
    cls_name = model.names[cls_id]
    conf = float(box.conf[0].item())
    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(w, x2), min(h, y2)
    crop = image[y1:y2, x1:x2]
    crop_name = f'{cls_name}_{idx}.jpg'
    crop_path = os.path.join(CROPS_DIR, crop_name)
    cv2.imwrite(crop_path, crop)
    detected_items.append({'id': idx, 'type': cls_name, 'confidence': round(conf, 3), 'bbox': {'x': x1, 'y': y1, 'width': x2 - x1, 'height': y2 - y1}, 'crop_path': crop_path})
    print(f'  [{idx+1}] {cls_name} (Conf: {conf:.2f}) -> {crop_name}')
json_path = os.path.join(OUTPUT_DIR, 'layout.json')
with open(json_path, 'w') as f:
    json.dump({'image_size': {'width': w, 'height': h}, 'components': detected_items}, f, indent=4)
print(f'Done! Layout saved to {json_path}')