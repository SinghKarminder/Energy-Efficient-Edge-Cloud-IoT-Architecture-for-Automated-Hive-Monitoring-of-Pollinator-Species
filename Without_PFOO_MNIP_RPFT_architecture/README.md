# Real-Time Insect Detection & Logging System (YOLO-Only Version)

This repository contains a real-time insect detection and logging pipeline for fixed-focus field cameras.  
This version performs **YOLO-based full-frame detection only** and does **not** include the earlier PFOO, MNIP, or RPFT algorithms.

The system continuously captures frames, applies YOLO insect detection, saves frames with movement, and logs per-second insect counts into per-minute CSV files.

## Features

### Real-Time Video Capture
- High-resolution capture using GStreamer pipelines  
- Supports USB/UVC cameras (e.g., `/dev/video0`, `/dev/video1`)  
- Adjustable resolution & FPS (default: 1920×1080 @ 60 FPS)

### YOLO-Based Insect Detection
- Uses a custom YOLO model (`best.pt`)  
- Detects insects on full frames (no PFOO/MNIP/RPFT preprocessing)  
- Extracts bounding boxes and counts insects per frame

### Automatic Frame Saving
- Saves a JPEG image **only when insects are detected**  
- Filenames include timestamp and device serial ID

### Per-Second & Per-Minute Statistics
- Computes mean insect count per second  
- Saves a CSV file every minute in the format:  
  `count_DD-MM-YYYY_HH-MM_DEVICEID.csv`

### Fully Configurable
- Reads parameters from `/etc/entomologist/ento.conf`  
- Configurable parameters include:
  1. Device serial ID  
  2. Image storage path  
  3. CSV storage path  

## Code Overview

### Main Components
| Function | Description |
|----------|-------------|
| `MotionRecorder.start()` | Initializes the camera and routes frames to the processing loop |
| `process_img(frame)` | Performs YOLO detection and returns bounding boxes |
| `start_storing_img(frame)` | Saves images, updates counters, and manages per-second stats |
| `save_csv()` | Generates per-minute CSV logs |

## Debug Options
Edit at the top of the script:
- `FRAME_DEBUG = False` → Draw bounding boxes on saved frames  
- `LOG_DEBUG = False` → Print console logs  
- `USE_RGB_NORM = False` → RGB normalization (currently unused)  

## Notes
- This version **does not** use PFOO / MNIP / RPFT; only full-frame YOLO detection is performed.  
- Ensure the correct GStreamer camera device is connected.  
- Designed for edge devices (Jetson, ARM boards, etc.).
