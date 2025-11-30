# Sensor Provisioning - `boot.py`

This script is responsible for **AWS IoT Fleet Provisioning** of the device. It securely creates keys and certificates, registers the device (“Thing”) on AWS IoT Core, and saves the credentials locally for long-term usage.

---

## Overview

- Reads device configuration from `/etc/entomologist/ento.conf`.
- Checks if the device is already provisioned.
- Connects securely to AWS IoT using MQTT over TLS.
- Performs fleet provisioning:
  - **CreateKeysAndCertificate**
  - **RegisterThing**
- Saves long-term credentials (`certificate.pem.crt`, `private.pem.key`, `AmazonRootCA1.pem`) to `/etc/entomologist/cert/`.
- Updates device boot status after successful provisioning.

---

## Configuration

### `ento.conf`
This JSON file must contain:

```json
{
  "device": {
    "SERIAL_ID": "your_device_serial",
    "ENDPOINT_URL": "your_iot_endpoint",
    "PROVISION_STATUS": "False"
  }
}
```
## Configuration Parameters

- **SERIAL_ID** – Unique identifier for the device.  
- **ENDPOINT_URL** – AWS IoT endpoint (ARN).  
- **PROVISION_STATUS** – `True` if device is already provisioned; otherwise `False`.

---

## Key Functionalities

| Functionality                     | Description                                                                                       |
|----------------------------------|---------------------------------------------------------------------------------------------------|
| AWS IoT MQTT Connection           | Connects to AWS IoT securely using TLS and certificate-based authentication                       |
| CreateKeysAndCertificate          | Requests new device keys and certificate from AWS                                                 |
| RegisterThing                     | Registers the device (“Thing”) on AWS IoT Core using provisioning template                        |
| Save Credentials                  | Saves `certificate.pem.crt`, `private.pem.key`, and `AmazonRootCA1.pem` locally for long-term use |
| Update Boot Status                | Calls `update_boot_status()` to indicate successful provisioning                                   |


# update_boot_status.py

This script updates the boot status of the device and publishes it to the configured MQTT topic on AWS IoT.

---

## Overview

- Publishes the device boot status to an MQTT topic after successful provisioning or boot.
- Updates the `PROVISION_STATUS` in `/etc/entomologist/ento.conf` to `"True"` once the device is booted.

## Configuration

The script reads configuration from `/etc/entomologist/ento.conf`:

- `ENDPOINT_URL` – AWS IoT endpoint (ARN)
- `SERIAL_ID` – Unique device identifier

Certificates stored in `/etc/entomologist/cert/`:

- `AmazonRootCA1.pem`
- `certificate.pem.crt`
- `private.pem.key`

MQTT connection parameters:

- **Port:** 8883
- **Keep-alive interval:** 44 seconds
- **Topic:** `cameraDevice/<SERIAL_ID>/booted`

---

| Functionality       | Description                                                                                   |
|--------------------|-----------------------------------------------------------------------------------------------|
| MQTT Connection     | Connects securely to AWS IoT using TLS and certificate-based authentication                  |
| Publish Boot Status | Publishes a JSON payload `{"serialID": "<SERIAL_ID>", "bootStatus": True}` to the MQTT topic |
| Update Config       | Updates `PROVISION_STATUS` in `/etc/entomologist/ento.conf` to `"True"`                       |



