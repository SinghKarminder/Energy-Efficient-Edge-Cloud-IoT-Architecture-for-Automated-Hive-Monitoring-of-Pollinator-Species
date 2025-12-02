# Real-Time Bee Detection on Video Frames

This Python script performs bee detection on extracted video frames using a TensorFlow Lite (TFLite) model. It detects bees, draws bounding boxes around them, saves the annotated frames, and generates a CSV file with the bee count per frame.

---

## Features

- Uses a pre-trained TFLite model for bee detection.
- Processes frames sequentially from a folder.
- Draws bounding boxes and confidence labels on detected bees.
- Saves annotated frames to an output folder.
- Records the number of bees detected in each frame to a CSV file.
- Cleans up input frames after processing to save storage.
- Measures total processing time.

---

## Requirements

- Python 3.x
- OpenCV
- NumPy
- TFLite Runtime
- CSV module (built-in)
- Time and OS modules (built-in)

Install the required packages using pip:

```bash
pip install opencv-python numpy tflite-runtime
```
