# Energy-Efficient Edge Processing IoT Framework for Pollinator Species

This repository contains a complete IoT-based system for **real-time monitoring, detection, and logging of pollinator species**. It is designed for edge devices to efficiently process video and sensor data using a **YOLO-based detection pipeline** while maintaining **low power consumption** for long-term field deployment.

The repository is organized in a **modular structure**, with dedicated components for:

- **Sensor provisioning**
- **Data acquisition**
- **Video/frame processing**
- **Cloud integration and data upload**
- **Model management and configuration**

In addition, this repository provides a **minimal reproducibility package**—including essential code, configuration parameters, and sample data—so that developers and researchers can understand the workflow and **adapt or build their own embedded-system–based solutions** on microcontrollers, Single Board Computers (SBCs), or custom processors.

A **Single Board Computer (SBC)** is a compact, fully functional computer built onto a **single circuit board**, typically used in embedded, IoT, and edge-AI applications. An SBC integrates:

- **Processor (CPU)**
- **Memory (RAM)**
- **Onboard storage** or support for **SD/eMMC**
- **I/O interfaces** such as USB, HDMI, GPIO, CSI/DSI camera ports, and networking options

SBCs are capable of running full operating systems such as **Linux**, making them ideal for deploying real-time inference, sensor fusion, and edge-level processing applications.

### Common Examples of SBCs

- **Raspberry Pi**
- **NVIDIA Jetson Nano / Xavier NX**
- **i.MX8 multicore processor (Aplias iMX8)** – *the system and code in this repository were tested on this platform*

SBCs provide a powerful yet energy-efficient platform for IoT edge deployments, enabling real-time processing without relying on cloud-based computation.

---
## Repository Structure

| Folder | Description |
|--------|-------------|
| `Annonated_data_for_training` | Contains labeled and annotated datasets used for training insect/pollinator detection models. |
| `Camera_configurations` | Stores camera settings and configuration files for different deployment environments. |
| `Camera_testing` | Scripts and tools for testing camera setup, resolution, FPS, and detection pipelines. |
| `Cloud_upload` | Modules for uploading captured data and processed results to cloud storage or remote servers. |
| `Job_allocation` | Handles distributed task scheduling for cameras and sensors across multiple devices. |
| `Make_video_file` | Scripts to compile stored images into video files for review and analysis. |
| `Model_results` | Stores outputs from trained models including evaluation metrics, predictions, and logs. |
| `Models` | Trained YOLO models (`best.pt`) and related model weights for insect detection. |
| `On_Edge_TFLite` | Contains scripts and steps to integrate the NXP eIQ Machine Learning Layer into a Toradex-based Yocto build system for running TFLite-based inference on edge devices. |
| `Sensor_configuration` | Configuration files for connected camera sensor. |
| `Sensor_manager_console` | Web-based dashboard and control console for managing sensors and monitoring device status. |
| `Sensor_provision` | Scripts for provisioning new devices on AWS IoT, including boot scripts and certificate management. |
| `Synchronizer` | Handles time synchronization, periodic advertising, and data aggregation between edge devices. |
| `With_PFOO_MNIP_RPFT_architecture` | Implementation of insect detection pipeline using advanced algorithms (PFOO, MNIP, RPFT) for optimized detection. |
| `Without_PFOO_MNIP_RPFT_architecture` | YOLO-only version for direct full-frame detection without PFOO/MNIP/RPFT preprocessing. |


---

## Key Features

- **Edge Processing:** Optimized pipelines for low-power devices (ARM/Jetson boards).  
- **Real-Time Insect Detection:** YOLO-based and advanced detection pipelines (PFOO, MNIP, RPFT).  
- **Data Logging:** Per-second insect counts and per-minute CSV logs.  
- **Video Capture & Storage:** GStreamer-based pipelines for high-resolution video capture.  
- **Cloud Integration:** Automated upload of captured data and results to cloud servers.  
- **Sensor Monitoring:** Real-time monitoring of environmental parameters like temperature, humidity, light, and GPS location.  
- **Device Provisioning:** Secure AWS IoT provisioning with certificates and MQTT communication.  

---

## How to Use

1. **Configure sensors and camera** using the files in `Sensor_configuration` and `Camera_configurations`.  
2. **Provision edge devices** using scripts in `Sensor_provision`.  
3. **Start the monitoring pipeline** using the relevant scripts in `With_PFOO_MNIP_RPFT_architecture` or `Without_PFOO_MNIP_RPFT_architecture`.  
4. **Monitor sensors and video feeds** via the `Sensor_manager_console`.  
5. **Upload results to cloud** using `Cloud_upload`.  
6. **Review or generate videos** using `Make_video_file`.  
7. **Check model performance and outputs** in `Model_results`.  

---

## Debugging & Configuration

- Configuration files are mainly stored in `/etc/entomologist/ento.conf`.  
- Each folder contains a detailed `README.md` with folder-specific instructions.  

---

## Dependencies

- Python 3.x  
- OpenCV, GStreamer  
- YOLO (Ultralytics)  
- AWS IoT SDK (awscrt, awsiot)  
- paho-mqtt  
- Numpy, Rectangle-Packer  

## System Configuration Requirements

This repository has been tested on the **Aplias i.MX8 multicore processor**. To ensure correct execution and reproducibility of results, the following system configurations are recommended:

- **Processor:** Aplias i.MX8 multicore processor  
- **Operating System:** Customized Linux image deployed on the processor  
- **Dependencies:** All required libraries and dependencies are included or documented in the respective module folders  

> **Note:** Execution of the complete pipeline requires a **customized Linux image** configured for the processor. The repository provides a minimal code framework to execute the process and reproduce results.

## Execution Instructions

- Detailed execution steps for **each module** are provided separately within their respective folders in the form of `README.md` files.  
- Users should refer to these module-specific instructions to correctly set up, run, and test individual components of the system.  
- The overall pipeline execution involves sequentially running the modules according to the instructions provided in the respective folders.  

This repository serves as a **minimal framework**, enabling users to reproduce the results efficiently once the customized Linux image is deployed on the i.MX8 processor.

## Acknowledgements

This work was supported by the **IIT Ropar Technology and Innovation Foundation (iHub–AWaDH)** for the Agriculture and Water Technology Development Hub, established by the **Department of Science & Technology (DST), Government of India**, at the **Indian Institute of Technology Ropar** under the **National Mission on Interdisciplinary Cyber-Physical Systems (NM–ICPS)**.  
The hub aims to develop sustainable solutions and improve agricultural productivity.

---

## Authors

**Karminder Singh**  
Department of Electrical Engineering  
Indian Institute of Technology Ropar, Rupnagar 140001, India  
Email: `karminder.21eez0018@iitrpr.ac.in`

**Milanpreet Kaur**  
Department of Electrical Engineering  
Indian Institute of Technology Ropar, Rupnagar 140001, India  
Email: `milanpreet.19eez0017@iitrpr.ac.in`

**Dr. Suman Kumar**  
Department of Electrical Engineering  
Indian Institute of Technology Ropar, Rupnagar 140001, India  
Email: `suman@iitrpr.ac.in`

---

## License

This repository is released for academic and research use. Please cite appropriately if you use any part of this work.




