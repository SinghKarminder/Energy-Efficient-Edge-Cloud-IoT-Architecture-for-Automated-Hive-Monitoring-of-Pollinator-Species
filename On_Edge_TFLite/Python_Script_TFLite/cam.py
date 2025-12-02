import os
import warnings
import cv2
import numpy as np
import tflite_runtime.interpreter as tflite
import csv
import time

# Suppress warnings
warnings.filterwarnings('ignore')

# Get current working directory
cwd = os.getcwd()

# Start timer
start = time.time()

# Paths and parameters
MODEL_PATH = './best.tflite'  # TFLite model path
MODEL_NAME = 'best'
DETECTION_THRESHOLD = 0.05          # Minimum detection confidence threshold
INPUT_PATH = './frames/input{:03}.png'   # Input frames path pattern
OUTPUT_PATH = './frames/output{:03}.png' # Output frames path pattern

# List to store detected bees count per frame
bees_per_frame = []

# Load TFLite model
interpreter = tflite.Interpreter(model_path=MODEL_PATH)
interpreter.allocate_tensors()
signature_fn = interpreter.get_signature_runner()

# Initialize variables
detection_result_image, cnt = [], 0
_, input_height, input_width, _ = interpreter.get_input_details()[0]['shape']

# Shortcuts for frequently used functions
image_read = cv2.imread
image_resize = cv2.resize
expand_dims = np.expand_dims
uint8 = np.uint8
typecast = np.ndarray.astype
squeeze = np.squeeze
draw_rect = cv2.rectangle
draw_text = cv2.putText
fontt = cv2.FONT_HERSHEY_SIMPLEX
append_bees = bees_per_frame.append
save_image = cv2.imwrite

# Loop through frames
for i in range(0, 101):
    # Read input frame and convert to uint8
    img = image_read(INPUT_PATH.format(i)).astype(uint8)

    # Resize and expand dimensions to match model input
    resized_img = expand_dims(
        image_resize(img, (input_height, input_width), interpolation=cv2.INTER_LINEAR), 
        axis=0
    )
    
    # Run inference
    output = signature_fn(images=resized_img)
    
    # Get results
    count = int(squeeze(output['output_0']))
    scores = squeeze(output['output_1'])
    boxes = squeeze(output['output_3'])
    
    # Filter results by detection threshold
    results = [
        {'bounding_box': boxes[i], 'score': scores[i]} 
        for i in range(count) 
        if scores[i] >= DETECTION_THRESHOLD
    ]
    
    # Draw bounding boxes and labels on the image
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

    # Save output image
    save_image(OUTPUT_PATH.format(i), img)

    # Append number of bees detected in this frame
    append_bees(len(results))
    
    # Remove the processed input frame to save space
    os.remove(INPUT_PATH.format(i))

# Write bee counts per frame to CSV
write_csv = csv.writer
with open('counts', 'w') as myfile:
    wr = write_csv(myfile, delimiter='\n', quoting=csv.QUOTE_ALL)
    wr.writerow(bees_per_frame)

# End timer and print elapsed time
end = time.time()
print("Time taken:", end - start)
