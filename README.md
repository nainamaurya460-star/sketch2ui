
# 🚀 ASketch2UI — Hand-Drawn Sketch to UI Generator

An AI/Computer Vision powered backend pipeline that transforms hand-drawn wireframes and UI sketches into structured digital layouts with automated component detection.

---

## 📊 Project Status & Progress

| Phase | Module | Status | Completion Date |
| :--- | :--- | :---: | :---: |
| **Phase 1** | OpenCV Preprocessing & Shadow Removal | `COMPLETED ✅` | Week 1 |
| **Phase 1** | Contour Extraction & Bounding Boxes | `COMPLETED ✅` | Week 1 |
| **Phase 1** | FastAPI Core Processing Pipeline | `COMPLETED ✅` | Week 1 |
| **Phase 2** | UI Element Classification (Heuristics / YOLO) | `IN PROGRESS ⏳` | Week 2 |
| **Phase 3** | Spatial Hierarchy & Nesting Engine | `UPCOMING 📅` | Week 3 |
| **Phase 4** | Interactive Frontend Canvas & Code Export | `UPCOMING 📅` | Week 4 |

---

## 📅 1-Month Target Roadmap (Sprint Schedule)

### 🟢 Week 1: Core Foundation & Preprocessing Engine *(Completed)*
- [x] Set up clean modular backend structure (`FastAPI` + `OpenCV`).
- [x] Implemented continuous noise reduction, Gaussian blur, and adaptive thresholding.
- [x] Built image-reading fallbacks for cross-platform support (Windows/Linux).
- [x] Created `/api/v1/sketch/process` endpoint to output detected bounding boxes ($x, y, w, h$).

---

### 🟡 Week 2: UI Element Classification *(Current Focus)*
- [ ] Implement Heuristic Classifiers based on aspect ratio, area, and bounding box density.
- [ ] Integrate ML / YOLOv8 model trained on hand-drawn UI component datasets.
- [ ] Classify detected contours into labels (`button`, `input_field`, `card`, `image_placeholder`, `text`).
- [ ] Refactor API response schema to include component type and confidence scores.

---

### 🔵 Week 3: Spatial Hierarchy & Layout Engine
- [ ] Develop a Bounding Box Containment Algorithm to calculate parent-child relationships.
- [ ] Build UI Tree Structuring logic to map nested components (e.g., buttons inside cards).
- [ ] Standardize layout schema output into JSON format compatible with web canvases.

---

### 🟣 Week 4: Frontend Integration & Code Export
- [ ] Build interactive Web Canvas (React / Next.js) to render dynamic bounding box overlays.
- [ ] Add drag-and-drop, label editing, and repositioning tools on the UI canvas.
- [ ] Implement automated code generator (JSON to HTML/Tailwind CSS & React Components).
- [ ] Perform end-to-end integration testing and final deployment.

---

## 🛠️ Tech Stack

- **Backend Framework:** FastAPI
- **Computer Vision:** OpenCV, NumPy
- **Machine Learning (Planned):** YOLOv8, PyTorch
- **Frontend (Upcoming):** React / Tailwind CSS
