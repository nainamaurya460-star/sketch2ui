import os
import random
import shutil

train_dir = r"dataset\base_dataset\dataset_roboflow\dataset_roboflow\train"
val_dir = r"dataset\base_dataset\dataset_roboflow\dataset_roboflow\valid"

os.makedirs(val_dir, exist_ok=True)

# Find all images that have a corresponding .txt label
images = [f for f in os.listdir(train_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
labeled_images = [img for img in images if os.path.exists(os.path.join(train_dir, os.path.splitext(img)[0] + ".txt"))]

# Shuffle and split 20% for validation
random.seed(42)
random.shuffle(labeled_images)
split_count = int(len(labeled_images) * 0.20)
val_images = labeled_images[:split_count]

for img in val_images:
    txt = os.path.splitext(img)[0] + ".txt"
    # Move image
    shutil.move(os.path.join(train_dir, img), os.path.join(val_dir, img))
    # Move label
    shutil.move(os.path.join(train_dir, txt), os.path.join(val_dir, txt))

print(f"Validation split created successfully!")
print(f"Moved {len(val_images)} images and their label files to: {val_dir}")
