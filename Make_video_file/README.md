# cam.py — Motion-Triggered Video Recorder & Insect Activity Logger

`cam.py` is a high-performance camera processing script designed for continuous insect monitoring using fixed-focus industrial cameras.  
It performs **motion detection**, **per-minute count analytics**, **image/video storage**, and **CSV logging**, optimized for embedded Linux devices.

---

## Features

- Auto-detects active camera device (`/dev/video*`)
- Kills any process occupying the camera (via `fuser`)
- Captures high-FPS video using **GStreamer + OpenCV**
- Motion detection using **MOG2 background subtractor**
- Supports:
  - Saving images (JPG)
  - Saving videos (AVI)
  - Saving per-minute insect count CSV files
- Supports optional RGB-plane normalization
- Contour-based object detection (lightweight and fast)
- Fully configurable via `/etc/entomologist/ento.conf`

---

## Configuration File

The script reads device configuration from:
```
/etc/entomologist/ento.conf
```


Example:

```json
{
  "device": {
    "SERIAL_ID": "DO12345",
    "STORAGE_PATH": "/var/tmp/images/",
    "COUNT_STORAGE_PATH": "/var/tmp/counts/"
  }
}
```
# Runtime Behavior

This document explains how the camera processing system operates internally, including device detection, motion analysis, image/video saving logic, and CSV count logging.

---

## Camera Auto-Detection

The script automatically detects an available camera using:

`get_cam_deviceID()`

It performs the following steps:

- Scans:
  - `/dev/video0`
  - `/dev/video1`
  - `/dev/video2`
- If any device is **busy**, it kills the blocking PID using:
fuser -k /dev/videoX

- Initializes the camera using **OpenCV + GStreamer**
- Reads a test frame
- Returns the first device ID that successfully streams video

---

## Motion Detection Pipeline

Motion detection follows a multi-stage optimized pipeline:

1. (Optional) **RGB plane normalization**
2. Apply **MOG2 background subtractor**
3. Noise reduction using **median blur**
4. Morphological **opening and closing**
5. Contour extraction
6. Remove small/noise contours using:
   CONTOUR_AREA_LIMIT


8. Bounding box extraction
9. Generate motion flag

### Motion Processing Output

```python
hasMovement, processedFrame, bbox = process_img(frame)
```

# Motion Recorder

This Python script captures images or videos from a camera stream, detects motion, and logs per-minute object counts as CSV files.

---

## Saving Images or Videos

| Mode       | Condition                                   | Output Type |
|------------|--------------------------------------------|------------|
| JPG Images | `MAX_IMAGES_PERSEC = 1`                     | `.jpg`     |
| AVI Video  | `MAX_IMAGES_PERSEC > 1` and `SAVE_AS_VIDEO = True` | `.avi`     |

> Video files are saved every 1 second from accumulated frames.

---

## Per-Minute CSV Count Logging

At each clock minute boundary:

- Mean number of detected objects per second is calculated.
- Saved as a CSV file:  
  `count_DD-MM-YYYY_HH-MM_DEVICE.csv`

**CSV Columns:**

| Column      | Description             |
|------------|-------------------------|
| device_id  | Camera device ID        |
| time_frame | Time frame of recording |
| insect_count | Mean detected insects |

---

## Global Parameters

| Parameter           | Default | Description                        |
|--------------------|---------|------------------------------------|
| `FRAME_DEBUG`       | False   | Show bounding boxes                 |
| `LOG_DEBUG`         | True    | Enable logging                      |
| `USE_RGB_NORM`      | False   | Optional RGB normalization          |
| `MAX_IMAGES_PERSEC` | 2       | Frames saved per second             |
| `SAVE_AS_VIDEO`     | True    | Enable video recording mode         |

---

## MotionRecorder Class

| Attribute                | Description                                |
|--------------------------|--------------------------------------------|
| `VID_RESO`               | Camera stream resolution (default 1920×1080) |
| `FPS`                    | Capture speed (default 60 FPS)             |
| `subtractor`             | MOG2 motion subtraction object             |
| `fourcc`                 | DIVX codec for AVI video                   |
| `temp_img_for_video`     | Buffered frames for video writing          |
| `img_mean_permin_list`   | Stores per-minute mean insect counts       |

---

## Script Execution Flow

1. Create the class object:

```
MR = MotionRecorder()
```
Start capturing and processing:
```
MR.start()
```
Clean shutdown:

```
MR.end()
```

## Output Files

| Type      | File Naming Format                          |
|-----------|--------------------------------------------|
| Images    | `DD-MM-YYYY_HH-MM-SS-microsec_DEVICE.jpg` |
| Videos    | `DD-MM-YYYY_HH-MM-SS_DEVICE.avi`          |
| CSV Logs  | `count_DD-MM-YYYY_HH-MM_DEVICE.csv`       |

---

## Dependencies

- Python 3.x  
- OpenCV (`cv2`)  
- GStreamer  
- numpy  

---

## Running the Script

```bash
python3 cam.py
```

## Deploying to Device (SSH)
scp cam.py root@192.168.8.1:/usr/sbin/cam/cam.py
