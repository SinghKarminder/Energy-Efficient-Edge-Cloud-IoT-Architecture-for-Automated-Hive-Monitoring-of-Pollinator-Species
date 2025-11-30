# Real-Time Insect Detection & Logging System

This system provides a **real-time insect detection and logging pipeline** designed for fixed-focus cameras deployed in field environments. It captures frames, detects motion, applies YOLO-based species detection, stores relevant images, and logs per-second insect counts in CSV format.

---

## Key Features

- **Real-time video capture** using GStreamer (supports USB and UVC cameras)
- **Motion detection pipeline**:
  1. **PFOO** – Patch Filtration for Overlapping Objects
  2. **MNIP** – Merging Nearby Insect Patches
  3. **RPFT** – Rectangular Packed Frame Transformation
- **On-device edge processing** with YOLO for insect detection
- **Per-second insect count statistics**
- **Per-minute CSV generation**
- **Automatic saving of frames with detected movement**
- **Debug overlays** with bounding boxes
- **Configurable parameters** via `ento.conf`

---

## Debugging Options

Inside `cam.py`, you can configure:

| Option        | Description                                 | Default |
|---------------|---------------------------------------------|---------|
| `CROP_IMAGES` | Enable RPFT packed images                   | True    |
| `FRAME_DEBUG` | Draw bounding boxes on frames               | False   |
| `LOG_DEBUG`   | Print debug logs to console                 | True    |
| `USE_RGB_NORM`| Normalize RGB channels before processing   | False   |

---

## System Requirements

- **Operating System:** Linux-based environment (tested on Apilas iMX8 multicore processor)  
- **GStreamer Support:** Required plugins - `v4l2src`, `decodebin`, `videoconvert`  
- **YOLO Model:** Trained model file (`best.pt`) must be available
