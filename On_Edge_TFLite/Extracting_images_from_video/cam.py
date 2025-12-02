import cv2
import os
import time

st = time.time()

video_path = './vid1.avi'
frames_path = './frames'

video = cv2.VideoCapture(video_path)
cnt = 0

while True:
    image_exists, image = video.read()
    if image_exists:
        if not os.path.isdir(frames_path):
            os.makedirs(frames_path)
        cv2.imwrite(os.path.join(frames_path, 'input%03d.png' % cnt), image)
        cnt += 1
    else:
        break

video.release()
end = time.time()
print("Time taken:", end - st)

