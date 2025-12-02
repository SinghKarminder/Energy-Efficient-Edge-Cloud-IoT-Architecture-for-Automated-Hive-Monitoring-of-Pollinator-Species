#!/bin/bash
set -e

echo "=== Creating meta-ml layer ==="
bitbake-layers create-layer ../layers/meta-ml
bitbake-layers add-layer ../layers/meta-ml

echo "=== Removing example recipes ==="
rm -rf ../layers/meta-ml/recipes-example

echo "=== Copying meta-ml recipes ==="
cp -r /media/awadh/AWADH_Work/AI_on_Edge_march23/yocto-ml-build/meta-imx/meta-ml/recipes-* ../layers/meta-ml/

echo "=== Copying OpenCV recipe folder ==="
cp -r /media/awadh/AWADH_Work/AI_on_Edge_march23/yocto-ml-build/meta-imx/meta-bsp/recipes-support/opencv ../layers/meta-ml/recipes-libraries/

echo "=== Copying pybind11-native ==="
cp -r ../../meta-sca/recipes-python/python-pybind11-native ../layers/meta-ml/recipes-libraries/

echo "=== Copying CMake recipe ==="
cp -r ../../openembedded-core-kirkstone/meta/recipes-devtools/cmake ../layers/meta-ml/recipes-devtools/

echo "=== Removing conflicting CMake ==="
rm -rf ../layers/meta-openembedded/meta-oe/recipes-devtools/cmake

echo "=== Updating OpenCV backport reference ==="
sed -i \
 's/require recipes-support\/opencv\/opencv_4.5.2.imx.bb/require backports\/recipes-support\/opencv\/opencv_4.5.2.imx.bb/g' \
 ../layers/meta-ml/recipes-libraries/opencv/opencv_4.5.4.imx.bb

echo "=== Removing flatbuffers ==="
rm -rf ../layers/meta-openembedded/meta-oe/recipes-devtools/flatbuffers

echo "=== Adding COMPATIBLE_MACHINE flags ==="
for file in \
  "../layers/meta-ml/recipes-libraries/arm-compute-library/arm-compute-library_21.08.bb" \
  "../layers/meta-ml/recipes-libraries/tensorflow-lite/tensorflow-lite-vx-delegate_2.8.0.bb" \
  "../layers/meta-ml/recipes-libraries/tim-vx/tim-vx_1.1.39.bb" \
  "../layers/meta-ml/recipes-libraries/nn-imx/nn-imx_1.3.0.bb"
do
  echo 'COMPATIBLE_MACHINE:apalis-imx8 = "(apalis-imx8)"' >> "$file"
  echo 'COMPATIBLE_MACHINE:verdin-imx8mp = "(verdin-imx8mp)"' >> "$file"
done

echo "=== Updating ONNX Runtime configuration ==="
sed -i \
 's/PACKAGECONFIG_VSI_NPU:mx8-nxp-bsp   = "vsi_npu"/PACKAGECONFIG_VSI_NPU:mx8-nxp-bsp   = "vsi_npu"\nPACKAGECONFIG_VSI_NPU:verdin-imx8mp   = "vsi_npu"/g' \
 ../layers/meta-ml/recipes-libraries/onnxruntime/onnxruntime_1.10.0.bb

echo "=== Updating local.conf ==="
{
  echo 'IMAGE_INSTALL_append += "tensorflow-lite tensorflow-lite-vx-delegate onnxruntime"'
  echo 'IMAGE_INSTALL_append += "opencv python3-pillow v4l2-"'
  echo 'IMAGE_INSTALL_remove += "packagegroup-tdx-qt5 wayland-qtdemo-launch-cinematicexperience "'
  echo 'IMAGE_INSTALL_append += "packagegroup-tdx-graphical packagegroup-fsl-isp v4l-utils"'
  echo 'SCA_DEFAULT_PREFERENCE ?= "-1"'
  echo 'PARALLEL_MAKE="-j 18"'
  echo 'BB_NUMBER_THREADS="18"'
  echo 'ACCEPT_FSL_EULA = "1"'
} >> conf/local.conf

echo "=== Script Completed Successfully ==="
