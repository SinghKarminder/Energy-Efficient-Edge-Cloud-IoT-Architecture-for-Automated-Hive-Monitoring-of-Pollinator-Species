import cv2
import os
import time

# Start timer to measure execution time
st = time.time()

# Path to the input video
video_path = './vid1.avi'

# Directory to save extracted frames
frames_path = './frames'

# Open the video file
video = cv2.VideoCapture(video_path)

# Frame counter
cnt = 0

# Loop through video frames
while True:
    # Read a frame from the video
    image_exists, image = video.read()
    
    # If frame is successfully read
    if image_exists:
        # Create the frames directory if it doesn't exist
        if not os.path.isdir(frames_path):
            os.makedirs(frames_path)
        
        # Save the current frame as an image file
        cv2.imwrite(os.path.join(frames_path, 'input%03d.png' % cnt), image)
        
        # Increment frame counter
        cnt += 1
    else:
        # Break the loop if no more frames
        break

# Release the video object
video.release()

# End timer and print the total time taken
end = time.time()
print("Time taken:", end - st)


