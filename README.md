# EmptyEye Project

**Smart Electricity Conservation System**

EmptyEye is an intelligent monitoring system that detects when fans or air conditioners are running in empty rooms and alerts administrators to save electricity. Using computer vision and machine learning, it helps reduce energy waste and lower electricity bills.

## Project Overview

The main goal of this project is to **save electricity** by:
- Detecting when fans or AC units are ON in empty rooms
- Identifying if humans are present in the monitored area
- Sending real-time alerts to administrators
- Providing a web-based dashboard for monitoring

## Features

- **Real-time Detection**: Uses YOLO models to detect:
  - AC units (ON/OFF status)
  - Ceiling fans (ON/OFF status)
  - Human presence in rooms
- **Web Dashboard**: Flask-based interface for monitoring
- **Alert System**: Email notifications when appliances are running in empty rooms
- **Video Streaming**: Live camera feed with detection overlays
- **User Management**: Signup, login, and password recovery
- **Notification History**: Track all alerts and system events

## Technology Stack

- **Backend**: Python Flask
- **Computer Vision**: YOLO (You Only Look Once) v11
- **Database**: MySQL
- **Frontend**: HTML/CSS/JavaScript
- **Libraries**:
  - OpenCV for image processing
  - Ultralytics YOLO for object detection
  - MySQL Connector for database operations
  - Flask-SocketIO for real-time communication

## Project Structure

```
EmptyEyeProject/
├── app.py                 # Main Flask application
├── db_config.py          # Database configuration
├── email_utils.py        # Email notification utilities
├── notification_utils.py # Notification management
├── requirements.txt      # Python dependencies
├── models/              # YOLO model files
│   ├── ac/             # AC detection model
│   └── ceiling_fan/    # Fan detection model
├── scripts/            # Detection modules
│   ├── ac.py          # AC detection logic
│   ├── ceiling-fan.py # Fan detection logic
│   ├── human.py       # Human detection logic
│   └── mobile-phone.py # Phone detection logic
├── static/            # CSS, JS, images
├── templates/         # HTML templates
└── yolo11*.pt        # Pre-trained YOLO models
```

## Installation

### Prerequisites
- Python 3.8+
- MySQL Server
- Webcam or IP camera
- SMTP email account (for notifications)

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd EmptyEyeProject
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Database Setup**
   - Install MySQL and create a database
   - Update `db_config.py` with your database credentials
   - Run the database setup script:
   ```bash
   python recreate_db.py
   ```

4. **Configure Email Settings**
   - Update email configuration in `email_utils.py`
   - Set up SMTP credentials for notifications

5. **Model Setup**
   - Ensure YOLO model files are in the correct directories:
     - `models/ac/best.pt` for AC detection
     - `models/ceiling_fan/weights/best.pt` for fan detection
     - `yolo11n.pt` for human detection

## Usage

1. **Start the application**
   ```bash
   python app.py
   ```

2. **Access the web interface**
   - Open your browser and go to `http://127.0.0.1:5000`
   - Create an account or log in

3. **Monitor your space**
   - The system will automatically detect appliances and humans
   - View live video feed with detection overlays
   - Receive email alerts when appliances are on in empty rooms

## How It Works

1. **Camera Input**: The system captures video from a connected camera
2. **Object Detection**: YOLO models analyze each frame to detect:
   - AC units and their ON/OFF status
   - Ceiling fans and their ON/OFF status
   - Human presence
3. **Logic Processing**: If appliances are detected as ON but no humans are present, an alert is triggered
4. **Notification**: Administrators receive email notifications about energy waste
5. **Dashboard**: Real-time status and history available through the web interface

## Configuration

### Detection Sensitivity
Adjust detection confidence in the respective script files:
- `scripts/ac.py`: Modify `conf=0.2` parameter
- `scripts/ceiling-fan.py`: Modify `conf=0.2` parameter
- `scripts/human.py`: Adjust detection parameters

### Email Notifications
Configure email settings in `email_utils.py`:
- SMTP server details
- Sender email credentials
- Notification recipients

## API Endpoints

- `/` - Home dashboard
- `/signup` - User registration
- `/login` - User authentication
- `/video_feed` - Live video stream
- `/detection_status` - Current detection status (JSON)
- `/notifications` - Notification history

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is designed for educational and energy conservation purposes.

## Troubleshooting

### Common Issues

1. **Camera not detected**
   - Check camera connections
   - Verify camera permissions
   - Test with `python test_cam.py`

2. **Model loading errors**
   - Ensure model files are in correct paths
   - Check file permissions
   - Verify model compatibility

3. **Database connection issues**
   - Verify MySQL service is running
   - Check database credentials in `db_config.py`
   - Ensure database exists

4. **Email notifications not working**
   - Verify SMTP settings
   - Check email credentials
   - Test email configuration

## Support

For issues and questions:
- Check the troubleshooting section
- Review error logs in the console
- Ensure all dependencies are properly installed
