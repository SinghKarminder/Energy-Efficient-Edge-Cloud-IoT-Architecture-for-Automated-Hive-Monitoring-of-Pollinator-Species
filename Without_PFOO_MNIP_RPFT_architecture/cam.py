'''
@camera_type: Fixed Focus


@abstract: frames individually, mean count, csv .... 

@dscp:  this code creates csv every minute with mean_count of every seconds        
        also saves images in which movement is detected

'''

# use this to display bounding boxes
FRAME_DEBUG = False

# use this to show on console when files are created
LOG_DEBUG = False

#us RGB plane normalization
USE_RGB_NORM = False
#---------------------

import cv2
import numpy as np
from datetime import datetime
import json
import logging as log
import csv
import subprocess
from ultralytics import YOLO

log.basicConfig(filename='/var/tmp/cam.log', filemode='w', level=log.INFO, format='[%(asctime)s]- %(message)s', datefmt='%d-%m-%Y %I:%M:%S %p')
log.info("Cam script started..")
with open(f"/etc/entomologist/ento.conf",'r') as file:
    data=json.load(file)

DEVICE_SERIAL_ID = data["device"]["SERIAL_ID"]
BUFFER_IMAGES_PATH = data["device"]["STORAGE_PATH"]
BUFFER_COUNT_PATH = data["device"]["COUNT_STORAGE_PATH"]

yolo_model = YOLO("/usr/sbin/detection/best.pt")

class MotionRecorder(object):
    
    # for Fixedfocus
    VID_RESO, FPS = (1920,1080), 60
    #VID_RESO, FPS = (1920,1200), 55
    #VID_RESO, FPS = (1280,720), 120
    #VID_RESO, FPS = (1280,720), 60   

    # video capture : from device    
    cap = cv2.VideoCapture(f"v4l2src device/dev/video2 ! video/x-raw, width={VID_RESO[0]}, height={VID_RESO[1]}, framerate={FPS}/1, format=(string)UYVY ! decodebin ! videoconvert ! appsink", cv2.CAP_GSTREAMER)
    

    # the background Subractors
    subtractor = cv2.createBackgroundSubtractorMOG2(detectShadows=False)    

    # FourCC is a 4-byte code used to specify the video codec. The list of available codes can be found in fourcc.org.
    fourcc = cv2.VideoWriter_fourcc(*'DIVX')     
    
    CONTOUR_AREA_LIMIT = 10
    
    img_mean_persec_list = []    
    img_count_sum = 0
    img_count = 0
    # for storing frames as collection of 1 sec
    last_minute = None
    last_second = None

    def _init_(self):
        pass

    def get_cam_deviceID(self, VID_RESO, FPS):

        # fetch which ever camera is working
        for i in range(0,3):
            # first stop the device --if busy

            output = None
            pid = -1
            try:        
                output = subprocess.check_output(["fuser",f"/dev/video{i}"])                
            except:
                if LOG_DEBUG:
                    print(f"No working cam at: /dev/video{i}")
                pass
            
            if output:
                output = output.decode('utf-8')
                try:
                    pid = int(output)
                    # kill the busy process
                    subprocess.call(["kill","-9",f"{pid}"])
                except:
                    pass

            # get camera output
            camera = cv2.VideoCapture(f"v4l2src device=/dev/video{i} ! video/x-raw, width={VID_RESO[0]}, height={VID_RESO[1]}, framerate={FPS}/1, format=(string)UYVY ! decodebin ! videoconvert ! appsink", cv2.CAP_GSTREAMER)
            while True:
                success, frame = camera.read()  # read the camera frame
                camera.release()
                if not success:                
                    break
                else:
                    if LOG_DEBUG:
                        print(f"Found working cam at: /dev/video{i}")
                    return i

        return -1

 def process_img(self, frame):
    """
    YOLO-based detection on full frame.
    Returns:
        hasMovement -> True if YOLO detected objects
        frame       -> original frame (not modified)
        detections  -> list of [x, y, w, h] for each YOLO detection
    """

    results = yolo_model(frame)[0]  # run YOLO on full frame
    detections = []

    for box in results.boxes:
        conf = float(box.conf[0])
        if conf < 0.5:
            continue  # discard low confidence
        
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        w = x2 - x1
        h = y2 - y1

        detections.append([x1, y1, w, h])

    hasMovement = len(detections) > 0

    # optional: debug boxes
    if FRAME_DEBUG:
        for x, y, w, h in detections:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    return hasMovement, frame, detections


    def start_storing_img(self, img):
        
        hasMovement, img2, bbox = self.process_img(img)
        if FRAME_DEBUG:
            img = img2
            #hasMovement = True

        # get current time
        now = datetime.now()

        # if change in minutes
        if self.last_minute == None:
            self.last_minute = now.minute
        elif self.last_minute != now.minute:
            # if sec changes, save last second count data            
            self.save_csv(now)
            #reset all
            self.last_minute = now.minute
            self.img_mean_persec_list = []
            self.img_count_sum = 0
            self.img_count = 0

        
        if hasMovement:

            # save image file
            self.temp_image_name = f'{now.strftime("%d-%m-%Y_%H-%M-%S-%f")}_{DEVICE_SERIAL_ID}.jpg'
            #self.save_recording(img)
            cv2.imwrite(BUFFER_IMAGES_PATH + self.temp_image_name, img)
            if LOG_DEBUG: print('Saved Image: ', self.temp_image_name, len(bbox))

            # assign count data                        
            self.img_count_sum += len(bbox)
            self.img_count += 1


        # if a change in second then append mean
        # save mean every second
        if self.last_second == None:
            self.last_second = now.second
        elif self.last_second != now.second:
            # if sec changes, save last second count data            
            
            if self.img_count != 0:
                mean_count_persec = self.img_count_sum // self.img_count
            else:
                mean_count_persec = 0

            self.img_mean_persec_list.append((DEVICE_SERIAL_ID, now.strftime("%d-%m-%Y_%H-%M-%S"), mean_count_persec))
            
            #reset all
            self.last_second = now.second                
            self.img_count_sum = 0
            self.img_count = 0
            
    
    def save_csv(self, timeNow):
        # save as count_timeFrame_deviceID_countMeanInt.csv
        # save as count_DD-MM-YYYY_hh-mm_DOxxx_XXXX.csv

        csvName = f'count_{timeNow.strftime("%d-%m-%Y_%H")}-{self.last_minute}_{DEVICE_SERIAL_ID}.csv'
        with open(BUFFER_COUNT_PATH + csvName, 'w',  newline='') as csvFile:
            csvwriter = csv.writer(csvFile)
            # header
            csvwriter.writerow(["device_id","time_frame","insect_count"])        
            # data 
            csvwriter.writerows(self.img_mean_persec_list)
    
        log.info("Video bbox count CSV crealog.info("")ted and saved -> "+csvName)
        if LOG_DEBUG: print('CSV saved', csvName)
            
            


    def save_recording(self, image):
        pass
        #cv2.imwrite(BUFFER_IMAGES_PATH+self.temp_image_name, image)

            
    def start(self):
        camID = -1
        while camID == -1:
            camID = self.get_cam_deviceID(self.VID_RESO, self.FPS)
        self.cap = cv2.VideoCapture(f"v4l2src device=/dev/video{camID} ! video/x-raw, width={self.VID_RESO[0]}, height={self.VID_RESO[1]}, framerate={self.FPS}/1, format=(string)UYVY ! decodebin ! videoconvert ! appsink", cv2.CAP_GSTREAMER)
        log.info("Cam started functioning")

        #fCount = 0

        while True :
            available, frame = self.cap.read()

            if available:                
                self.start_storing_img(frame)

                # check exit
                if cv2.waitKey(1) & 0xFF == ord('x'):
                    break
            else:
                if FRAME_DEBUG:
                    print("...Device Unavailable");

    def end(self):        
        self.save_recording()
        self.cap.release()
        cv2.destroyAllWindows()


# main
MR = MotionRecorder()
log.info("Object created")
MR.start()
MR.end()
log.info("Script ended")

# to send this file over ssh to device 
# scp {source_path} root@192.168.8.1:/usr/sbin/cam/cam.py
# scp /home/tif-awadh/Desktop/gitCodes/ARJUN/Final_Codes/allFrameCapture/cam.py root@192.168.8.1:/usr/sbin/cam/cam.py
# scp /home/tif-awadh/Desktop/local_see3cam_test/device_code/microseconds/cam.py root@192.168.8.1:/usr/sbin/cam/cam.py
