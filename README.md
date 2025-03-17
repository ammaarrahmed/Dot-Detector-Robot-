# Dot-Detector-Robot-
Vision-Guided Servo Tracking System
https://youtu.be/oHfYfc69wVg
This project is a computer vision-powered servo tracking system that detects circular markers (dots) on a live video feed using OpenCV, calculates their positions, and sends commands to an ESP32 microcontroller to physically track and align with the detected target. The ESP32 controls two servos that adjust angles based on the target's position.

Features:
Real-time dot detection using OpenCV's Hough Circle Transform
Calculates the closest dot to the center of the frame for targeting
Sends HTTP POST requests to the ESP32 to adjust servo angles
ESP32 web server endpoint for receiving angle updates and controlling servos
Smooth and adjustable tracking behavior via simple configuration
Tech Stack:
Python (OpenCV, requests)
ESP32 (Arduino framework)
Two-axis servo control
WiFi communication between PC and ESP32
Use Cases:
Automated object tracking system
Vision-guided robotics
AI-assisted turret or gimbal stabilization prototypes

