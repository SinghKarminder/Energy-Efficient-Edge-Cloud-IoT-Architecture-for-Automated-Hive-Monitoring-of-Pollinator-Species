# Sensor Manager Console

`sensor_manager_console` provides a web-based interface to monitor and manage device sensors, camera feeds, system stats, and configuration files.

The system is built using **Python Flask**, **OpenCV**, and standard Linux utilities for device management.

---

## Features

- User authentication with session-based login.
- Real-time video streaming from device cameras.
- Camera control through `v4l2-ctl` commands.
- Upload and download files to/from the device.
- System monitoring:
  - CPU, GPU, RAM usage
  - Battery parameters
  - Light intensity
  - Temperature and humidity
  - GPS location
  - Cellular connectivity
  - Storage usage
- Configuration management for `rana` service.
- REST endpoints for uploading files and setting camera controls.

---

## Requirements / Dependencies

- Python 3.x
- Flask
- OpenCV (`cv2`)
- Linux utilities:
  - `v4l2-ctl`
  - `fuser`
  - `subprocess` modules
- Device scripts in `/usr/sbin/device-manager/DeviceManager/`:
  - `job_data.sh`
  - `cellular.sh`
  - `storage_state.sh`

---

## Directory / File Structure

| File / Folder               | Description |
|-----------------------------|------------|
| `run.py`                    | Main Flask application. |
| `/media/mmcblk1p1`          | Upload folder for user files. |
| `/usr/sbin/rana`             | Folder for rana service and config uploads. |
| `/usr/sbin/rana/ranacore.conf` | Configuration file for rana service. |
| `/usr/sbin/device-manager/DeviceManager/credentials.json` | Stores login credentials. |

---

## Running the Application

1. Copy `run.py` to the target device:

```bash
scp run.py root@192.168.8.1:/usr/sbin/sensor_manager_console/run.py
```
2. Start the Flask app:

```
python3 run.py
```
3. Access the web interface in a browser:

```
http://<device-ip>:8000
```

## User Authentication

- **Login page:** `/`  
- **Credentials:** Stored in `/usr/sbin/device-manager/DeviceManager/credentials.json`  
- **Redirect:** Successful login redirects to the dashboard (`/dashboard`)  

---

## Video Streaming

| Endpoint       | Description                                         |
|----------------|-----------------------------------------------------|
| `/video_feed`  | Streams live camera feed (requires login)          |
| `/video`       | Shows camera control parameters and allows adjustments |

**Camera Controls:**  

- `/setCamControls?key=<control>&value=<value>` — Update camera parameters via query string.

---

## Dashboard

- **Endpoint:** `/dashboard`  
- **Displays real-time system statistics including:**
  - CPU, GPU, RAM usage
  - Temperature and humidity
  - Battery info
  - Light intensity
  - GPS location
  - Storage usage
  - Internet connectivity

---

## File Management

| Endpoint          | Description                                         |
|------------------|-----------------------------------------------------|
| `/files`          | Lists uploaded files                                |
| `/files/<filename>` | Download a specific file                           |
| `/upd`            | Upload files via web form                            |
| `/uploader`       | API endpoint for file upload to rana folder         |

---

## Configuration Management

| Endpoint                     | Description                                  |
|-------------------------------|---------------------------------------------|
| `/configurations`             | View and edit `rana` configuration          |
| `/saveRanaConfig`             | Save updated configuration                   |
| `/configurations/file`        | Download the configuration file             |

---

## Notes

- Flask server runs on `0.0.0.0:8000` by default.  
- Ensure device scripts (`job_data.sh`, `cellular.sh`, `storage_state.sh`) have execute permissions.  
- Video capture uses OpenCV with GStreamer backend for better device compatibility.  
- Session-based authentication is required for all sensitive endpoints.

---

## Example Deployment

```bash
scp /home/user/sensor_manager_console/run.py root@192.168.8.1:/usr/sbin/sensor_manager_console/run.py
python3 /usr/sbin/sensor_manager_console/run.py
