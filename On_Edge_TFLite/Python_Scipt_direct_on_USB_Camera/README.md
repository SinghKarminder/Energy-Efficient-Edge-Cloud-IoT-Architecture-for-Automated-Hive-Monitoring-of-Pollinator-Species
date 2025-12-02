# Real-Time Bee Detection Using Live Camera Feed

This Python script performs real-time bee detection using a TensorFlow Lite (TFLite) model on a live camera feed. Detected bees are annotated with bounding boxes and confidence scores, and frames are saved periodically for further analysis.

---

## Features

- Uses a pre-trained TFLite model for bee detection.
- Captures live video from a camera (Video4Linux device).
- Processes every 60th frame to balance performance.
- Draws bounding boxes and confidence labels on detected bees.
- Saves annotated frames to an output folder.
- Prints processing time per frame for performance monitoring.

---

## Requirements

- Python 3.x
- OpenCV
- NumPy
- TFLite Runtime
- Time, OS, CSV, and sys modules (built-in)

Install required Python packages using pip:

```bash
pip install opencv-python numpy tflite-runtime
```
