## 1. imageUpload.py

This module handles **uploading captured images** from the device to the cloud using **pre-signed URLs**.

### Key Responsibilities
- Reads device serial number and storage path from `ento.conf`
- Loads `signedUrls.json` containing:
  - Filenames to upload  
  - Corresponding pre-signed upload URLs (AWS S3-style)
- Uploads each file using HTTP POST multipart upload
- Provides status logs for each upload

### Important Functions
#### **upload_file(filename, response)**
- Opens the image file from the device buffer
- Sends it to the cloud using `requests.post()`
- Prints HTTP response code or error

#### **image_upload_manager()**
- Waits 3 seconds to ensure system readiness  
- Loads all pre-signed URLs from `signedUrls.json`  
- Iterates through provided file list and uploads each one  
- Prints start and completion banners

### Required Files
- `/etc/entomologist/ento.conf` (contains device SERIAL_ID, STORAGE_PATH)
- `signedUrls.json` (created by jobreceiver or cloud service)

### Purpose
Ensures **reliable, secure, chunk-free image upload** from edge device → cloud using server-issued signed URLs.

## 2. move.py

This script handles **batch movement of captured images** from the temporary camera repository into the upload buffer. It ensures controlled, orderly processing before cloud upload.

### Key Responsibilities
- Monitors `cameraImageRepo/` for new files
- Moves files in **batches of 5** into `bufferStorage/`
- After each batch, triggers `main()` from `run.py` to process/upload

### Workflow
1. Read all filenames from `cameraImageRepo/`
2. While files exist:
   - Take the first 5 (or fewer if less than 5 remain)
   - Move each file to `bufferStorage/`
   - Log movement action
3. After each batch, call:
   ```python
   main()  # from run.py
`
   ## 3. run.py

This script manages **MQTT-based publishing** of file metadata (typically filenames or upload instructions) to the cloud. It is used by the upload pipeline after image batches are moved.

### Key Responsibilities
- Establishes a secure MQTT connection using TLS certificates  
- Publishes payloads (e.g., file lists, upload triggers) to the specified topic  
- Works together with `sub.py` for subscription operations  

### Core Workflow
1. **Initialize MQTT client**
   - Uses AWS IoT–style TLS certificates:
     - Root CA
     - Device certificate
     - Private key  
2. **Connect to MQTT Broker**
3. **Publish Payload**
   - Topic, QoS, and payload are supplied externally via:
     ```python
     start_publish(...)
     ```
4. **Wait for callback**
   - `on_connect()` → confirms connection, triggers publishing  
   - `on_publish()` → logs success & disconnects  

### Function: `start_publish()`
Arguments:
- `broker`, `port`, `interval`
- `clientName`
- `topic`, `qos`, `payload`
- `rootCA`, `cert`, `privateKey`

Purpose:
- Configure client  
- Retry connection until successful  
- Publish data securely  
- Keep connection alive using `loop_forever()`

### Purpose
Enables **secure MQTT communication** for triggering cloud uploads, reporting available files, and synchronizing with the cloud infrastructure.

## 4. sub.py

This script handles the **MQTT subscription** side of the cloud-upload system.  
It listens for **signed URLs** sent from the cloud and stores them locally for `imageUpload.py` to use.

### Key Responsibilities
- Connect securely to the MQTT broker via TLS  
- Subscribe to a topic that returns **signed URLs** for uploading images  
- Save the received payload to `signedUrls.json`  
- Work in coordination with `run.py` and `imageUpload.py`  

### Core Workflow
1. **Initialize secure MQTT client**
   - Load AWS IoT–style certificates:
     - Root CA  
     - Device Certificate  
     - Private Key  
2. **Subscribe to topic**
3. **Receive cloud payload**
   - Signed URLs in JSON format  
4. **Store payload locally**
   - Writes directly to:  
     ```
     signedUrls.json
     ```
5. **Auto-disconnect after receiving URLs**

### Callback Details
- `on_connect()`  
  Subscribes to the configured topic when MQTT connection is established.

- `on_message()`  
  - Decodes payload  
  - Saves it to `signedUrls.json`  
  - Disconnects the client  

### Function: `start_subscribe()`
Arguments:
- `broker`, `port`, `interval`
- `clientName`
- `topic`, `qos`
- `rootCA`, `cert`, `privateKey`

Purpose:
- Create secure MQTT subscriber  
- Retry connection until successful  
- Wait indefinitely to receive signed URLs  

### Purpose
This module enables the device to **receive upload permissions (signed URLs)** from the cloud securely, completing the two-way cloud synchronization flow.

## 5. **verification.py — Image Upload Verification Module**

`verification.py` ensures that every uploaded image is **verified by the server** before it is deleted locally.  
It listens to an MQTT verification topic and removes only the successfully confirmed files.

---

## Core Functions

### Delete verified images  
Removes the file from buffer storage only after the server confirms successful upload.

### Track batch progress  
Counts how many images in the current batch have been verified.

### Auto-disconnect  
Once the full batch is verified, the MQTT client disconnects automatically.

---

## Configuration

The script loads the buffer storage path from:

```with open("/etc/entomologist/ento.conf",'r') as file:
    data = json.load(file)
BUFFER_IMAGES_PATH = data["device"]["STORAGE_PATH"]
This defines where images are stored before verification and deletion.
```

## Global Variables

```python
uploaded = 0        # Number of verified files
batchSize = 0       # Total files expected in the batch
TOPIC = None        # MQTT topic to subscribe to
QoS = None          # MQTT QoS level
```
 ### on_message() — Handling Verification Messages

def on_message(client, userdata, message):
    recievedPayload = message.payload.decode('utf-8')
    recievedPayload = ast.literal_eval(recievedPayload)

    filename = recievedPayload['file']
    os.remove(BUFFER_IMAGES_PATH + filename)
    
### What this function does:
Receives the verification payload from the server

Parses the JSON-like content

Extracts the filename

Deletes the corresponding file from buffer storage

Increments the internal verification counter

Disconnects once the entire batch is verified

### on_connect() — Subscribing to Topic

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.subscribe(TOPIC, QoS)
Subscribes to the verification topic as soon as MQTT connection is successful.

### start_verification() — Main Function

def start_verification(
        broker, port, interval, clientName,
        topic, qos, batch_size, rootCA, cert, privateKey):
        
## Parameters

| Parameter    | Description |
|-------------|-------------|
| **broker**       | AWS IoT MQTT endpoint |
| **port**         | MQTT TLS port (e.g., `8883`) |
| **interval**     | Keepalive interval for MQTT client |
| **clientName**   | MQTT client ID used for connection |
| **topic**        | MQTT topic used for verification publishing |
| **qos**          | MQTT Quality of Service level |
| **batch_size**   | Expected number of uploaded files for verification |
| **rootCA**       | Path to AWS IoT Root CA certificate |
| **cert**         | Path to AWS IoT device certificate |
| **privateKey**   | Path to AWS IoT private key |


### Tasks performed:
Sets global batch size, topic, and QoS

Initializes a secure MQTT client connected with AWS IoT Core

Registers callbacks (on_connect, on_message)

Subscribes and listens until the batch is fully verified

## Guarantees Provided by verification.py
Prevents accidental deletion — files are removed only after server confirmation

Ensures reliability via batch-based verification

Maintains security using AWS IoT Core TLS-based MQTT

Handles automation by disconnecting automatically after completion

