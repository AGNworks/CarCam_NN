# Smart Autonomous Car Control with Computer Vision

<p align="center" width="400px" height="240px">
  <img src="https://github.com/AGNworks/CarCam_NN/blob/main/assets/pictures/car_moving.gif" alt="result"/>
</p>

## Project Overview
This project implements an autonomous control system for a robotic car using computer vision and a U-Net neural network. The system processes live camera feed to recognize tracks and make navigation decisions.

## Key features
  - Computer Vision Pipeline: Real-time image processing with a custom U-Net model
  - Raspberry Pi Integration: Optimized for embedded deployment
  - Web Interface: Browser-based control and video streaming

## Hardware Implementation
### Current Robot Design
<p align="center">
  <img src="https://github.com/AGNworks/CarCam_NN/blob/main/assets/pictures/1.png" alt="actual version"/>
</p>

The current design, inspired by Tim Clark's model from [Thingiverse](https://www.thingiverse.com/thing:700835), offers improved stability and controllability compared to the initial prototype:

<p align="center">
  <img src="https://github.com/AGNworks/CarCam_NN/blob/main/assets/pictures/2.png" alt="old version"/>
</p>

## Data Collection
### 1. Image Capture ([code](https://github.com/AGNworks/CarCam)):
 - Manual control of robot movements (forward/backward/left/right)
 - Automatic image saving after each movement

### 2. Dataset Preparation:
  - Manual segmentation using GIMP
  - Automated post-processing to ensure clean masks ([code](https://github.com/AGNworks/Image-segmentation-with-GIMP/blob/main/y_generator.py))
  - Validation scripts to check data quality

<p align="center">
  <img src="https://github.com/AGNworks/CarCam_NN/blob/main/assets/pictures/3.png" alt="segmented picture"/>
</p>

## Neural Network Performance
The U-Net model demonstrates effective track recognition:

<p align="center">
  <img src="https://github.com/AGNworks/CarCam_NN/blob/main/assets/pictures/4.png" alt="result"/>
</p>

## Raspberry Pi Setup
### Dependency Installation
After cloning the repository from github, go to project folder. This project uses Poetry for dependency management. Install all required dependencies with:
```bash
# Install project dependencies (system-wide without virtualenv)
poetry config virtualenvs.create false
poetry install
```

### Autostart Configuration
Set up the system to run the python code after boot.
Edit the profile configuration:
```bash
sudo nano /etc/profile
```
Add these lines in the end of the file
```bash
# Wait wifi to connect
while [ "$(ifconfig wlan0 | grep inet | grep 192.168.)" = ""  ]; do sleep 1; done

# Change to the project directory
cd /path/to/your_project_directory

# And start the main.py
sudo python main.py
```

Useful commands for testing
```bash
# Check GPU memory allocation
vcgencmd get_mem gpu

# Check installed dependencies
poetry show

# Add new dependencies
poetry add package_name
```

## System Demonstration
<p align="center">
  <img src="https://github.com/AGNworks/CarCam_NN/blob/main/assets/pictures/CarCam.gif" alt="test"/>
</p>

## API Documentation
### API Endpoints

| Endpoint        | Description                      | Content Type                      |
|-----------------|----------------------------------|-----------------------------------|
| `/`             | Main control interface           | HTML                              |
| `/video_feed`   | Raw camera stream                | `multipart/x-mixed-replace`       |
| `/seg_feed`     | NN-processed video stream        | `multipart/x-mixed-replace`       |
| `/process`      | Control command handler          | JSON                              |


### Control Commands
Send POST requests to /process with JSON payload:

- **"R"**:  Start autonomous movement
- **"S"**:  Stop all movement
- **"C"**:  Toggle neural network processing

## Future Enhancements
1. Improved model performance with larger dataset
2. Obstacle detection and avoidance
3. Speed adaptive control
4. Advanced path planning algorithms
5. Multi-camera support for 360° perception

## Repository Structure
```
CarCam_NN/
├── app/
│   ├── camera.py      # Video capture and processing
│   ├── robot.py       # Motor control interface
│   ├── params.py      # Fixed parameters used in functions
│   └── router.py      # Web API endpoints
├── assets/
│   └── pictures/      # Documentation images
│   └── models/        # Neural network models
├── templates/         # Web interface templates
├── static/            # Web interface static files
├── main.py            # Main
└── README.md          # Project documentation
```
