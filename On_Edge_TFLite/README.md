# Adding the eIQ Layer to the Yocto Build

This document provides clear and reproducible steps to integrate the **NXP eIQ Machine Learning Layer (`meta-imx/meta-ml`)** into a Toradex-based Yocto build system.  
It includes instructions for cloning the Toradex BSP, adding ML-related layers, setting up the environment, building the image, and resolving common issues.

---

## 1. Cloning the Toradex BSP

Create the Yocto build directory and initialize the Toradex BSP repository.  
This repository forms the base Yocto environment on top of which the ML layer is added.

```bash
mkdir -p ./yocto-ml-build/bsp-toradex && cd ./yocto-ml-build/bsp-toradex
repo init -u https://git.toradex.com/toradex-manifest.git -b refs/tags/5.7.0-devel-202206 -m tdxref/default.xml
repo sync
```

## 2. Adding the eIQ Layer

To integrate **NXP’s eIQ Machine Learning software**, clone the required Yocto layers into your build environment:

```bash
git clone --depth 1 -b kirkstone-5.15.32-2.0.0 git://source.codeaurora.org/external/imx/meta-imx ../meta-imx
git clone --depth 1 -b dunfell https://github.com/priv-kweihmann/meta-sca.git ../meta-sca
git clone --depth 1 -b kirkstone git://git.openembedded.org/openembedded-core ../openembedded-core-kirkstone
```

### Repository Breakdown

| Repository          | Description                                                   |
|---------------------|---------------------------------------------------------------|
| **meta-imx**        | NXP BSP layer containing **eIQ Machine Learning** support     |
| **meta-sca**        | Static Code Analysis tools                                    |
| **openembedded-core** | Core OpenEmbedded components (Kirkstone branch)            |

These layers add NXP ML capabilities, development utilities, and the essential OpenEmbedded metadata required for building extended Toradex BSP images.


# Yocto Build Instructions for Toradex i.MX8

This repository provides the basic steps required to set up the Yocto build environment, add custom layers, and compile images for Toradex i.MX8 platforms.

---

## 3. Setting Up the Build Environment

Initialize the Yocto and BitBake environment using the Toradex setup script:

```bash
source ./export
```

# `setup_TF_layer.sh` – Yocto ML Layer Setup Script

This script automates the creation and configuration of a **Yocto meta-ml layer** for Toradex i.MX8 platforms, including machine learning libraries, OpenCV, TensorFlow Lite, ONNX Runtime, and related dependencies.

---

## **File:** `setup_TF_layer.sh`

### **Purpose**

- Create a custom **meta-ml** layer.
- Copy and organize ML-related recipes.
- Remove conflicting or unnecessary recipes.
- Update recipes for target machines (`apalis-imx8`, `verdin-imx8mp`).
- Configure OpenCV, TensorFlow Lite, ONNX Runtime, and other ML dependencies.
- Update `local.conf` with required packages and build parameters.

---

### **Usage**

1. Make the script executable:

```bash
chmod +x setup_TF_layer.sh

