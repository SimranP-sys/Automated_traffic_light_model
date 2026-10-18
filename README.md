# Trafficlight-

A smart traffic-light control project that adjusts signal timing based on real-time traffic density. The system combines computer vision, a microcontroller, and a mobile dashboard to detect vehicle flow and switch the traffic lights automatically.

## Overview

This project simulates a traffic junction where signal timing changes according to traffic pressure rather than fixed intervals. A camera captures the road, a Python script analyzes the scene using OpenCV, and the result is sent to an ESP32 controller that drives the traffic lights and updates a Blynk dashboard.

The system is designed to:
- detect traffic density in each lane using image processing,
- classify the situation as LOW or HIGH traffic,
- alter signal timing dynamically,
- display live traffic status through a dashboard,
- control physical LEDs connected to the ESP32.

## Project idea

Instead of using a fixed timer for all traffic conditions, this project uses live vehicle density to decide whether a lane should remain green for longer or a shorter time. The controller tries to reduce waiting time on busy roads while still keeping the system simple and reliable for a small prototype.

## Circuit diagram

<img width="1408" height="768" alt="ckt diagram" src="https://github.com/user-attachments/assets/6f14e194-35d2-4b83-8beb-c3f0a6a7f14e" />

## Working concept

1. A camera stream provides live road footage.
2. The Python program (`one.py`) processes the video frame and identifies moving vehicles in the selected lanes.
3. Based on the detected count, the system decides whether traffic is LOW or HIGH.
4. That decision is transmitted over serial to the ESP32.
5. The ESP32 code (`one.ino`) updates the signal states and drives the LEDs.
6. A Blynk dashboard shows the current lane status and density.

## Hardware used

- ESP32 development board
- Traffic signal LEDs (green, yellow, red)
- 7-segment display for countdown/indicator output
- Resistors and wiring for LED connections
- Camera module / IP camera source for live traffic input
- Breadboard and power supply for prototype testing

## Software used

- Python 3
- OpenCV for traffic detection
- PySerial for communication with the ESP32
- Arduino IDE for ESP32 firmware
- Blynk for live signal monitoring dashboard

## Repository structure

- `one.py` — OpenCV-based vehicle detection and traffic density analysis
- `one.ino` — ESP32 firmware to control traffic lights and communicate with Blynk
- `README.md` — project documentation

## Example output

The dashboard shows a live density reading and signal states. In the screenshots below, the system identifies traffic as LOW or HIGH and updates the corresponding light conditions automatically.

<img width="1832" height="1087" alt="Screenshot 2026-10-14 211354" src="https://github.com/user-attachments/assets/e32f0f9a-336d-4d38-bfc4-7f18e0253781" />
<img width="1897" height="1165" alt="Screenshot 2026-10-14 211526" src="https://github.com/user-attachments/assets/7577ac69-1f6b-4af4-ab29-3e076ad79be7" />
<img width="1919" height="1179" alt="Screenshot 2026-10-14 211426" src="https://github.com/user-attachments/assets/cc94fe88-3987-43bf-af79-f2ff9edf0c0b" />

## Notes

This project is a prototype for adaptive traffic management. It demonstrates how image-based vehicle counting can be used to make traffic lights respond to actual road conditions instead of fixed cycles.

## Future improvements

- Support more than two lanes
- Add real-time queue length estimation
- Improve detection robustness in different lighting conditions
- Use cloud or local database logging for traffic history
- Add a more advanced controller algorithm for signal optimization

