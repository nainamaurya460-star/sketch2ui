import os
import csv
from collections import defaultdict

# Paths
csv_path = r"dataset\base_dataset\dataset_roboflow\dataset_roboflow\new_trainannotations.csv"
train_dir = r"dataset\base_dataset\dataset_roboflow\dataset_roboflow\train"

# Class mapping according to dataset.yaml
classes = [
    "Button", "CheckBox", "Heading", "Image", "Label",
    "Link", "Paragraph", "RadioButton", "Select", "TextBox"
]
class_to_id = {cls_name: idx for idx, cls_name in enumerate(classes)}

# Group annotations by image_name
grouped_annotations = defaultdict(list)

with open(csv_path, mode="r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        img_name = row["image_name"].strip()
        grouped_annotations[img_name].append(row)

converted_count = 0

for img_name, rows in grouped_annotations.items():
    txt_name = os.path.splitext(img_name)[0] + ".txt"
    txt_path = os.path.join(train_dir, txt_name)

    lines = []
    for r in rows:
        c_name = r["class_name"].strip()
        if c_name not in class_to_id:
            continue

        cid = class_to_id[c_name]
        w_img = float(r["width"])
        h_img = float(r["height"])
        xmin = float(r["x_min"])
        ymin = float(r["y_min"])
        xmax = float(r["x_max"])
        ymax = float(r["y_max"])

        # Calculate normalized YOLO format
        x_center = ((xmin + xmax) / 2.0) / w_img
        y_center = ((ymin + ymax) / 2.0) / h_img
        bbox_w = (xmax - xmin) / w_img
        bbox_h = (ymax - ymin) / h_img

        lines.append(f"{cid} {x_center:.6f} {y_center:.6f} {bbox_w:.6f} {bbox_h:.6f}")

    if lines:
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        converted_count += 1

print(f"Done! Converted YOLO label files created for {converted_count} images.")
