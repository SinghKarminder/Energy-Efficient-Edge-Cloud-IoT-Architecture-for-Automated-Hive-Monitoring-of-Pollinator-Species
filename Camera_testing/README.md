# Camera Motion Recorder (cam.py)

This module continuously reads frames from the camera, detects motion using background subtraction, and saves short video clips whenever movement is detected.  
It is designed for field devices where lightweight motion-triggered recording is required.

---

# Features

- Auto-detects camera model (USB Cam / MIPI CSI camera)
- Uses **GStreamer pipelines** for video capture
- Applies **Gaussian blur + MOG2 background subtraction**
- Detects motion using a histogram threshold
- Records only when motion occurs
- Saves output as `.avi` videos (DIVX codec)
- Automatically closes video segments when motion stops

---

# File: `cam.py`  
Below is an explanation of how the script works.

---

# 1. Camera Detection & Initialization

The script automatically checks which camera model is connected by reading:

/sys/class/video4linux/*/name

Based on the name, it selects the appropriate GStreamer pipeline:

| Camera Model | Selected Pipeline |
|--------------|------------------|
| USB Camera ("Video Capture 4") | Uses `/dev/video2` (UYVY format → BGR) |
| MIPI CSI Camera ("mxc-mipi-csi2.1") | Uses BGRx → BGR pipeline |
| Unknown | Prints "No Camera found" |

---

# 2. Motion Detection Logic

Motion detection steps:

1. Read frame  
2. Apply **Gaussian Blur** → reduces noise  
3. Apply **BackgroundSubtractorMOG2**  
4. Extract white pixels count from mask histogram  
5. If histogram value > `hist_threshold` (500):  
   - Motion detected → store frame  
6. If motion stops for 5 consecutive frames:  
   - Finalize and save the current video clip  

---

# 3. Video Recording

- Frames stored during motion → kept in memory  
- When motion stops → saved as:

YYYYMMDDHHMMSS.avi

