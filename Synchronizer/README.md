# Synchronizer Service — Device Operation Controller (synchronizer.py)

synchronizer.py is the central controller service that manages the operational state of the entomologist device.
It monitors provisioning status, handles automatic scheduling, manages TEST mode, and controls all system services (cam, cloud, weather, systeminfo-sd, jobreceiver).

This script ensures that the device always runs in the correct mode depending on time, provisioning state, and user configurations stored in ento.conf.

# Key Responsibilities
## 1. Provisioning Management
- The script continuously monitors:
      "PROVISION_STATUS": "True"
- As long as provisioning is incomplete, it repeatedly executes:
      /usr/sbin/provision/boot.py
- Only after provisioning succeeds does the system proceed
  to the main loop and begin normal operation.
## 2. TEST Mode Handling
- If TEST_FLAG = "True":
      • Restart cam and cloud services
      • Run the device in continuous operation for TEST_DURATION minutes
- After TEST mode completes:
      • TEST_FLAG is automatically reset to "False"
      • Device returns to normal scheduled operation

This enables remote/OTA-triggered testing without manual intervention.


## 3. ON/OFF Timer Scheduling

The synchronizer reads the following time window from `ento.conf`:


The `compareTime()` function determines whether the current system time falls **within the active operating window**.

### When the current time is *within* the ON→OFF interval:
- Start **cam** (insect detection)
- Start/Restart **weather** service
- Start/Restart **systeminfo-sd** (system metrics logger)
- Stop **cloud** service (prevents uploads during active capture)
- Set internal script status to **active**

### When the current time is *outside* the ON→OFF interval:
- Stop **cam**
- Stop **weather**
- Stop **systeminfo-sd**
- Restart **cloud** (uploads all pending images & CSV files)
- Set internal script status to **inactive**

This mechanism ensures **fully automated daily scheduling**, enabling the device to capture data only during configured hours while uploading and synchronizing during off-hours.


## Services Managed

| Service Name     | Purpose                                      |
|------------------|----------------------------------------------|
| **cam**          | Starts the camera capture & insect detection |
| **cloud**        | Uploads saved frames & CSV to server         |
| **weather**      | Gathers temperature/humidity/wind data       |
| **systeminfo-sd**| Logs CPU, RAM, and storage statistics        |
| **jobreceiver**  | Handles OTA jobs and remote commands         |
| **provision/boot.py** | Runs only until the device is provisioned |

# File Interactions
## Modifies

/etc/entomologist/ento.conf

/etc/entomologist/scriptStatus.json

## Logs

/var/tmp/sync.log

# Script Workflow

## 1. Startup Sequence
- Wait 10 seconds (device stabilization)
- Set internal flags:
    • TEST_FLAG = False
    • status = False (stored in scriptStatus.json)
- Run provisioning workflow
- Start background services:
    • cloud        → uploads frames & CSV
    • jobreceiver  → handles OTA jobs & commands
- Enter main loop
## 2. Main Loop Logic (runs every 5 seconds)
1. Read latest device configuration (ento.conf)

2. Check operating mode:
    - If TEST mode = ON:
          → run test-mode handler
    - Else:
          → follow ON/OFF schedule

3. Manage services:
    - Start/stop system services based on schedule/mode

4. Update script status file (scriptStatus.json)
## Function Summary
Provides robust, real-time orchestration of device services,
ensuring reliable automation, scheduling, configuration syncing,
and remote manageability.

