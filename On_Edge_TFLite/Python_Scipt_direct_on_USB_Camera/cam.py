import os
import warnings
import cv2
import numpy as np
import tflite_runtime.interpreter as tflite
import csv
import time
import timeit
import sys

# Suppress warnings
warnings.filterwarnings('ignore')

# Current working directory
cwd = os.getcwd()

# Open camera (Video4Linux device)
cap = cv2.VideoCapture("/dev/video2", cv2.CAP_V4L)

# TFLite model configuration
MODEL_PATH = './model2apis.tflite'
MODEL_NAME = 'model2apis'
DETECTION_THRESHOLD = 0.05  # Minimum confidence to consider a detection

# Output path pattern for saving processed frames
OUTPUT_PATH = './frames1/output{:03}.png'

# Load TFLite model
interpreter = tflite.Interpreter(model_path=MODEL_PATH)
interpreter.allocate_tensors()
signature_fn = interpreter.get_signature_runner()

# Get model input shape
_, input_height, input_width, _ = interpreter.get_input_details()[0]['shape']

# Shortcuts for commonly used functions
image_resize = cv2.resize
expand_dims = np.expand_dims
uint8 = np.uint8
typecast = np.ndarray.astype
sqee = np.squeeze  # Typo in original code: "sqee" should be "squeeze"
draw_rect = cv2.rectangle
draw_text = cv2.putText
fontt = cv2.FONT_HERSHEY_SIMPLEX
save_image = cv2.imwrite

# Check if the camera opened successfully
if cap.isOpened():
    ctr = 0  # Frame counter

    while True:
        # Read a frame from the camera
        ret_val, img = cap.read()
        start = time.time()

        # Process every 60th frame
        if ctr % 60 == 0:
            img = img.astype(uint8)  # Convert frame to uint8

            # Resize and expand dimensions for model input
            resized_img = expand_dims(
                image_resize(img, (input_height, input_width), interpolation=cv2.INTER_LINEAR),
                axis=0
            )

            # Run inference
            output = signature_fn(images=resized_img)
            count = int(sqee(output['output_0']))
            scores = sqee(output['output_1'])
            boxes = sqee(output['output_3'])

            # Filter results based on detection threshold
            results = [
                {'bounding_box': boxes[i], 'score': scores[i]} 
                for i in range(count) 
                if scores[i] >= DETECTION_THRESHOLD
            ]

            # Draw bounding boxes and labels on the frame
            for obj in results:
                ymin, xmin, ymax, xmax = obj['bounding_box']
                xmin = int(xmin * img.shape[1])
                xmax = int(xmax * img.shape[1])
                ymin = int(ymin * img.shape[0])
                ymax = int(ymax * img.shape[0])

                draw_rect(img, (xmin, ymin), (xmax, ymax), (255, 0, 0), 1)
                y = ymin - 15 if ymin - 15 > 15 else ymin + 15
                label = "{}: {:.0f}%".format('APIS', obj['score'] * 100)
                draw_text(img, label, (xmin, y), fontt, 0.5, (0, 0, 0), 1)

            # Save annotated frame
            save_image(OUTPUT_PATH.format(ctr // 60), img)

        # Print processing time for current frame
        end = time.time()
        print(end - start)

        # Increment frame counter
        ctr += 1

        # Add a short delay to allow GUI updates (not strictly necessary if not displaying)
        cv2.waitKey(1)

else:
    print("Camera open failed")

# Release camera and destroy any OpenCV windows
cap.release()
cv2.destroyAllWindows()
