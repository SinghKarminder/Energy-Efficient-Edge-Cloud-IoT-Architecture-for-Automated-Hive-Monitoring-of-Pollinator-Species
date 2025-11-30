# Camera Configuration Module

This folder contains all files responsible for configuring the camera hardware during device boot.  
The module uses **v4l2-ctl** to apply camera parameters such as brightness, contrast, exposure, focus, and zoom.

---

# Files Overview

## `cam_set.py`
Python script that reads all camera parameters from `camera_control.conf` and applies them to `/dev/video2` using `v4l2-ctl`.

### **Workflow**
1. Load configuration from `/etc/entomologist/camera_control.conf`
2. Iterate through each parameter (brightness, contrast, focus, etc.)
3. Apply each setting to the camera using:
   v4l2-ctl --device /dev/video2 --set-ctrl=<param>=<value>
4. Add a small delay (0.5s) after each setting for hardware stability

### **Usage**
The script is automatically executed by the systemd service:
sudo systemctl restart camera_set


---

## `camera_set.service`
Systemd service responsible for running `cam_set.py` at boot.

### **Service Key Functions**
- Runs **after** `devdetect.service` to ensure the camera is detected  
- Executes `/usr/sbin/camera/cam_set.py` using Python3  
- Automatically restarts on failure  

### **Enable on Boot**
```bash
sudo systemctl enable camera_set.service
sudo systemctl start camera_set.service
```

# `camera_control.conf`

A JSON configuration file containing all adjustable camera parameters.

