# Heartly Detector
The Heartly project aims to create an user-friendly device that monitors the cardiovascular health through hear rate (HR) and heart rate variability (HRV) analysis. The objective was to provide individuals with a practical tool to gain insights into their physiological condition and support preventative healthcare.

The device was constructed by using the Raspberry Pi Pico microcontroller, a Crowtail Pulse Sensor, and the OLED display. Photoplethysmography (PPG) was employed to detect changes in blood volume, while the Kubios software was utilized for the HRV analysis. The data were collected from the Pulse Sensor, processed by the microcontroller, and displayed on the OLED screen. 

![heartly](https://github.com/user-attachments/assets/6632944c-4958-465f-8116-83cc78471b41)

## Features
* Measure and near real-time drawing of Heart rate (updated every 5 seconds)
* Measure and calculate HRV
* Measure and send PPIs to Kubios to process and return HRV results
* View history of measurements
* Integrated with Kubios via MQTT and Kubios Proxy
* Connection to WiFi and MQTT to send data
* Engaging and user-friendly interface
* LEGO-built case for stable ground when used

## Sneak-peak
<img width="1379" alt="image" src="https://github.com/user-attachments/assets/3805820d-a03b-4540-b3fb-e46d82e39ecf" />

_Screens of the program_

![welcome3](https://github.com/user-attachments/assets/db2a81a9-e603-4de0-8286-bbd8a139347a)

_Welcoming screen_

## Installation
### Components needed
- Raspberry Pi Pico
- Crowtail Pulse Sensor
- OLED Display(SSD1306 I2C 128x64 pixels)
- Rotary Encoder
 
### Hardware setup
Simply connect the wire to your computer. Every hardware set up is already been done within the case.
 
### Software setup
1. Install ```mpremote```if it is not already installed
```

pip install mpremote
```

2. Go to the folder where you want to save the repository for this device
```

cd <your-path>
```
3. Clone the repository
```

git clone --recurse-submodules https://github.com/anhhuy-ux/Heartly-Project
```
4. Go to the main repository of Heartly
```

cd Heartly-project
```
6. Configure WiFi setting, go to src/action.py
* Adjust SSID, PASSWORD according to the WiFi you use

<img width="498" alt="image" src="https://github.com/user-attachments/assets/f0cca2ac-c044-4076-bae7-49f5a58364b8" />


5. Run the script

If you use Linux/MacOS:
```

./install.sh
```
If you use Window
```

./install.cmd
```
6. Restart the Raspberry Pi Pico
7. Enjoy!
### Usage
1. Run the run-me.py
2. The device will start running
3. Navigate through the main menu using the rotary encoder(rotate to move selection, press to choose) for different mode:
  - HR: measure heart rate
  - HRV: measure and calculate HRV
  - Kubios: measure and send to Kubios to calculate
  - History: view past measurements
4. Select the desired mode

### Acknowledgement
- Teammates in building this project: [Tamseela Mahmood](https://github.com/tamseelaa), [Taysa Abinader](https://github.com/TaysaAbinader), [Lan-Anh Tran](https://github.com/anhlt13), [Anh Huynh](https://github.com/anh-tq-huynh)
- Professor Sakari Lukkarinen - For the SOS model for filtering data read from the sensor

### Appendix
- [Product teaser](https://youtu.be/bljx0XSSEbo)
- [Product demo(SPEED UP)](https://youtu.be/7VWpicF_zvc)
  ![thumbnail](https://github.com/user-attachments/assets/19d1a654-c4e6-4c1e-be06-14d9cb46708b)

_Product Image_

![image](https://github.com/user-attachments/assets/d3d1b952-69f2-4e25-a6d0-54eb72a5dacf)

_Code structure_

<img width="425" alt="image" src="https://github.com/user-attachments/assets/76f88a16-0436-49e7-a2a9-bf4f9e0e647c" />

_Program Workflow_
