# 1. jobReceiver.py

`jobReceiver.py` is the primary **MQTT-based job-handling service** running on the entomologist edge device.  
It manages cloud-to-device communication, device configuration, sensor control, image capture, and job execution using AWS IoT Core.

---

## 1. Features

### Core Responsibilities
- Receive **cloud-triggered jobs** via AWS IoT MQTT topics  
- Handle **device/data/camera/RANA configuration requests**  
- Perform **image capture + upload to S3 (via signed URL)**  
- Execute **RANA engine configuration updates**  
- Update camera settings using **v4l2-ctl**  
- Generate and upload **device statistics**  
- Manage **multi-threaded execution** for all operations  
- Maintain **TLS-secured MQTT communication**  

---

## 1.1 Workflow Overview

`jobReceiver.py` performs the following sequence:

1. **Load device configuration**
   - Reads `/etc/entomologist/ento.conf` to obtain:
     - SERIAL_ID  
     - MQTT Endpoint URL  
     - Bucket info  
     - Local storage paths  

2. **Initialize secure MQTT client**
   - Uses certificates:
     - `AmazonRootCA1.pem`
     - `certificate.pem.crt`
     - `private.pem.key`

3. **Subscribe to AWS IoT topics**
   - `cameraDevice/job/<SERIAL_ID>`  
   - `declient/<SERIAL_ID>/data/req`  
   - `declient/<SERIAL_ID>/config/req`  
   - `declient/<SERIAL_ID>/image/req`

4. **Process inbound messages**
   - Each category (data/config/image/job) is dispatched to its **own thread**  
     - Avoids blocking  
     - Enables parallel tasks  

5. **Perform actions**
   - Device statistics generation  
   - Image capture (`cv2.VideoCapture`)  
   - Upload image using signed S3 URL  
   - Read/update RANA configuration  
   - Read/update camera controls  
   - Persist device/job configuration locally  

6. **Send response back to cloud**
   - Publishes to:
     - `<SERIAL_ID>/data/resp`
     - `<SERIAL_ID>/config/resp`
     - `<SERIAL_ID>/image/resp`
     - `<SERIAL_ID>/job/resp`

---

## 1.2 Major Functional Blocks

### Job Parsing  
Updates:
- Time Zone  
- Device ON/OFF duration  
- Test mode  
- Job ID  

### Image Processing  
- Captures JPEG frame  
- Uploads through signed URL (HTTP PUT)  
- Sends success/failure acknowledgement  

### Device Stats Collection  
Collects:
- MAC / IP address  
- Storage info  
- Modem data  
- GPS  
- System logs  

### Camera Control Management  
Reads & updates:
- Exposure  
- Brightness  
- Gain  
- Other V4L2-supported controls

---

## 1.3 MQTT Topics

### Subscribed Topics
| Topic | Description |
|-------|-------------|
| `cameraDevice/job/<SERIAL_ID>` | Receive job commands |
| `declient/<SERIAL_ID>/data/req` | Device/RANA/Camera data requests |
| `declient/<SERIAL_ID>/config/req` | Configuration update commands |
| `declient/<SERIAL_ID>/image/req` | Request to capture and upload image |

### Published Topics
| Topic | Purpose |
|-------|---------|
| `declient/<SERIAL_ID>/data/resp` | Response payloads for data queries |
| `declient/<SERIAL_ID>/config/resp` | Acknowledgement of config updates |
| `declient/<SERIAL_ID>/image/resp` | Image upload status |
| `declient/<SERIAL_ID>/job/resp` | Job acknowledgement/status |

---

## 1.4 Important Paths

| Path | Purpose |
|------|---------|
| `/etc/entomologist/ento.conf` | Main device configuration |
| `/etc/entomologist/camera_control.conf` | Camera control state |
| `/usr/sbin/rana/ranacore.conf` | RANA engine configuration |
| `/tmp/` | Temporary device stats & network info |
| `/usr/sbin/jobreceiver/test_image.jpeg` | Captured image file |

---

## 1.5 Key Dependencies

- Python `paho.mqtt.client`
- `requests`
- `cv2` (OpenCV)
- `json`
- `threading`
- `subprocess`
- `v4l2-ctl` (camera control interface)

---

# 2. logsUpload.py

`logsUpload.py` is responsible for uploading device logs stored in `/var/tmp/` to an AWS S3 bucket using an API Gateway endpoint.

---

## 2.1 Features
- Reads bucket name from `/etc/entomologist/ento.conf`
- Scans `/var/tmp/` for all log files
- Uploads files using:

HTTP PUT → API Gateway → S3 bucket

- Prints HTTP status for each upload

---

## 2.2 Workflow

1. Read device config  
2. Extract bucket name  
3. Enumerate files from `/var/tmp/`  
4. Upload each file using:  

```
https://<api-url>/<bucket>/<filename>
```
5. Print success/error  

---

## 2.3 Usage

`logsUpload.upload_log_file()` is called automatically when the cloud sends a `"Get-All-Logs"` request in a job.

---
