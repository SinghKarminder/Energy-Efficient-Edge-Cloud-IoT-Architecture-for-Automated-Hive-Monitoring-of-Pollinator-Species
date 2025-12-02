import cv2
import os
import time
st = time.time()
video_path = './vid1.avi'
frames_path = './frames'
video = cv2.VideoCapture(video_path)
while True:
image_exists, image = video.read()
cnt = 0
while image_exists is True:
if not os.path.isdir(frames_path):
os.makedirs(frames_path)
cv2.imwrite(frames_path+'/input%03d.png'%cnt, image)
image_exists, image = video.read()
cnt += 1
else:
break
end=time.time()
print(end-st)
