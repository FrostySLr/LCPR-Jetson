# License Plate Recognition System using Jetson Nano with Computer Vision and OCR
## Description
This project is a smart license plate detection and recognition system using Jetson Nano, Vehicle Loop Detector, and a USB Webcam. In this project, I use NoMachine to share the screen of the Jetson Nano on my laptop (which is what the USB Wi-Fi adapter is for). However, it will also work if connected to a monitor or TV.
<br/>

I will be using Faster R-CNN for license plate detection, PaddleOCR for text extraction from the plate, and Vehicle Loop Detector for vehicle detection. 
<br/>
Big Thanks to Qengineering for the unofficial upgrade for the Jetson Nano!  (Link to their page: https://qengineering.eu/)
## Libraries
- At least Python 3.8
- Pytorch CUDA (For Jetson: 1.13, For Training: <2.0)
- PaddlePaddle >=2.10
- Dataset: https://universe.roboflow.com/plat-nomor-indonesia/plat-nomor-indonesia-hdxeg (Version 3) (*If you want to use your dataset, all is good)
- OpenCV


## Components (HW)
**MicroComputer**  
- NVIDIA Jetson Nano 4GB using Ubuntu 20.04 (Link on how to upgrade your Jetson to 20.04: https://github.com/Qengineering/Jetson-Nano-Ubuntu-20-image)
<br/>

**Microcontroller**
- Arduino UNO<br/>

**Sensors**

- Vehicle Loop Detector (/w atleast a 3 meter coil cable) *I use a 2x1 loop

**Others**  

- USB Webcam (I use Logitech C922 for this project but it should work with most webcam)
- Wi-Fi USB
- NoMachine (to show the display of the Jetson Nano on your laptop's screen using the same Wi-Fi)
## Pin Layouts
<img src="images/skematik wiring diagram.png" height="450px">

## Documentation
**Photos**<br/>  
<img src="images/20250414_093248.jpg" height="450px"><br/>
<img src="images/20250414_092830.jpg" height="450px"><br/>
<img src="images/Test Project.jpg" height="450px"><br/>


**Video**  

https://github.com/user-attachments/assets/58235cc1-261f-4766-a8c4-3d316525e1dd








