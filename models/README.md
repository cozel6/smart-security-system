# AI Models Directory

This directory contains AI models for object detection.

## YOLOv5 Model

### Automatic Download

The YOLOv5 nano model will be **automatically downloaded** on first run.

No manual download required!

### Manual Download (Optional)

If automatic download fails, you can manually download:

```bash
cd models
wget https://github.com/ultralytics/yolov5/releases/download/v7.0/yolov5n.pt
```

### Model Information

**Model:** YOLOv5n (nano)
**Size:** ~3.8 MB
**Speed:** ~200-300ms per inference on Raspberry Pi 4
**Accuracy:** 75-85% on COCO dataset

**Classes Used:**
- Class 0: Person
- Class 15-23: Animals (bird, cat, dog, horse, sheep, cow, elephant, bear, zebra, giraffe)

### Verify Model

```bash
python3 -c "from src.detection.yolo_detector import YOLODetector; d = YOLODetector(); d.load_model(); print('Model loaded successfully!')"
```

### Alternative Models

You can use other YOLOv5 variants by changing `YOLO_MODEL` in `.env`:

- `yolov5n.pt` - Nano (fastest, recommended for Raspberry Pi)
- `yolov5s.pt` - Small (more accurate, slower)
- `yolov5m.pt` - Medium (not recommended for Pi 4)
- `yolov5l.pt` - Large (too slow for Pi 4)

### Model Cache

Once downloaded, models are cached here permanently.

**Do not commit model files to Git!** (Already in .gitignore)
