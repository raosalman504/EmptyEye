from flask import Flask, render_template, request, redirect, url_for, session, jsonify, Response, flash
import mysql.connector
from db_config import get_db_connection
import notification_utils
import os
import cv2
import threading
import time
import numpy as np
import importlib
import re
import dns.resolver
from email_utils import send_password_reset_email, send_username_reminder_email, generate_token, confirm_token

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['SERVER_NAME'] = '127.0.0.1:5000'  # Set this to your actual server name in production

# --- LOGIN & SIGNUP ROUTES ---
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        # Email validation - basic format check
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return render_template('signup.html', error='Please enter a valid email address')
        
        # Validate email domain
        domain = email.split('@')[1]
        
        # List of valid TLDs (top-level domains)
        valid_tlds = ['com', 'org', 'net', 'edu', 'gov', 'mil', 'io', 'co', 'us', 'uk', 'ca', 'au', 'de', 'jp', 'fr', 'it', 'ru', 'cn', 'in', 'br', 'info', 'biz', 'me']
        
        # Check if the domain has a valid TLD
        domain_parts = domain.split('.')
        if len(domain_parts) < 2 or domain_parts[-1].lower() not in valid_tlds:
            return render_template('signup.html', error='Please enter an email with a valid domain')
        
        # Try to validate the domain with DNS lookup (if dns.resolver is available)
        try:
            dns.resolver.resolve(domain, 'MX')
        except:
            # If DNS lookup fails, check if it's a common domain
            common_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'icloud.com', 'aol.com', 'protonmail.com', 'mail.com', 'zoho.com', 'yandex.com']
            if domain.lower() not in common_domains:
                return render_template('signup.html', error='Please enter an email with a valid domain')
        
        # Password strength validation
        if len(password) < 8:
            return render_template('signup.html', error='Password must be at least 8 characters long')
        
        # Check for at least one uppercase letter, one lowercase letter, and one number
        if not (re.search(r'[A-Z]', password) and re.search(r'[a-z]', password) and re.search(r'[0-9]', password)):
            return render_template('signup.html', error='Password must contain at least one uppercase letter, one lowercase letter, and one number')
        
        # Check if username already exists
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return render_template('signup.html', error='Username already exists')
        
        # Check if email already exists
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return render_template('signup.html', error='Email already exists')
        
        # All validations passed, insert the new user
        cursor.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)", 
                      (username, password, email))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user:
            session['username'] = username
            session['email'] = user['email']  
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('email', None)  
    return redirect(url_for('login'))

# --- PASSWORD RECOVERY ROUTES ---
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        
        # Check if email exists in database
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user:
            # Generate token
            token = generate_token(email)
            
            # Create password reset link
            reset_url = url_for('reset_password', token=token, _external=True)
            
            # Send email
            if send_password_reset_email(email, reset_url):
                return render_template('forgot_password.html', 
                                      success='Password reset link has been sent to your email.')
            else:
                return render_template('forgot_password.html', 
                                      error='Failed to send email. Please try again later.')
        else:
            # Don't reveal if email exists or not for security
            return render_template('forgot_password.html', 
                                  success='If this email is registered, you will receive a password reset link.')
    
    return render_template('forgot_password.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    # Verify token
    email = confirm_token(token)
    if not email:
        return render_template('reset_password.html', 
                              error='The password reset link is invalid or has expired.')
    
    if request.method == 'POST':
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Validate password
        if len(password) < 8:
            return render_template('reset_password.html', token=token,
                                  error='Password must be at least 8 characters long')
        
        if not (re.search(r'[A-Z]', password) and re.search(r'[a-z]', password) and re.search(r'[0-9]', password)):
            return render_template('reset_password.html', token=token,
                                  error='Password must contain at least one uppercase letter, one lowercase letter, and one number')
        
        if password != confirm_password:
            return render_template('reset_password.html', token=token,
                                  error='Passwords do not match')
        
        # Update password in database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password = %s WHERE email = %s", (password, email))
        conn.commit()
        cursor.close()
        conn.close()
        
        return render_template('login.html', 
                              success='Your password has been updated successfully. You can now log in with your new password.')
    
    return render_template('reset_password.html')

@app.route('/forgot_username', methods=['GET', 'POST'])
def forgot_username():
    if request.method == 'POST':
        email = request.form['email']
        
        # Check if email exists and get username
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT username FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user:
            # Send username reminder email
            if send_username_reminder_email(email, user['username']):
                return render_template('forgot_username.html', 
                                      success='Your username has been sent to your email address.')
            else:
                return render_template('forgot_username.html', 
                                      error='Failed to send email. Please try again later.')
        else:
            # Don't reveal if email exists or not for security
            return render_template('forgot_username.html', 
                                  success='If this email is registered, you will receive your username.')
    
    return render_template('forgot_username.html')

# --- HOME PAGE ---
@app.route('/')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('home.html')

# --- ABOUT PAGE ---
@app.route('/about')
def about():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('about.html')

# --- NOTIFICATION HISTORY ---
@app.route('/notifications')
def notifications():
    if 'username' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get notifications for current user's email
    email = session.get('email')
    cursor.execute("SELECT * FROM notifications WHERE recipient = %s ORDER BY timestamp DESC", (email,))
    
    notifications = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(notifications)

# --- DETECTION STATUS API ---
from scripts.ac import detect as ac_detect
from scripts.human import detect as human_detect
fan_detect = importlib.import_module('scripts.ceiling-fan').detect
mobile_detect = importlib.import_module('scripts.mobile-phone').detect

last_human_time = time.time()  # Initialize to current time
last_notification_time = time.time()  # Initialize to current time so first notification waits full 15 seconds
last_mobile_detected_time = 0  # When mobile was first detected in empty room
mobile_notification_sent = False  # Track if we've sent a notification for this mobile detection session
ac_first_detected_time = 0  # When AC was first detected in empty room
ac_notification_sent = False  # Track if we've sent a notification for AC in this session
fan_first_detected_time = 0  # When fan was first detected in empty room
fan_notification_sent = False  # Track if we've sent a notification for fan in this session
NOTIF_INTERVAL = 15  # seconds

# Store user info and detection status for active streams
active_streams = {}
detection_results = {
    'human_present': False,
    'ac_status': 'off',
    'fan_status': 'off',
    'mobile_present': False
}

# Helper function to check if email is a Gmail address
def is_gmail_address(email):
    if email and "@gmail.com" in email.lower():
        return True
    return False

@app.route('/detection_status')
def detection_status():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Return the actual detection results from the global variable
    return jsonify({
        'ac_status': detection_results['ac_status'],
        'fan_status': detection_results['fan_status'],
        'human_present': detection_results['human_present'],
        'mobile_present': detection_results['mobile_present']
    })

# --- VIDEO STREAMING AND DETECTION ---
@app.route('/video_feed')
def video_feed():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Store user email for notifications
    thread_id = id(threading.current_thread())
    active_streams[thread_id] = session.get('email')
    
    return Response(generate_video(), mimetype='multipart/x-mixed-replace; boundary=frame')

def generate_video():
    thread_id = id(threading.current_thread())
    try:
        cap = cv2.VideoCapture(0)
        global last_human_time, last_notification_time, last_mobile_detected_time, mobile_notification_sent
        global ac_first_detected_time, ac_notification_sent, fan_first_detected_time, fan_notification_sent
        global detection_results
        
        # Initialize detection times to current time
        current_time = time.time()
        last_human_time = current_time
        last_notification_time = current_time
        last_mobile_detected_time = 0
        ac_first_detected_time = 0
        fan_first_detected_time = 0
        
        while True:
            ret, frame = cap.read()
            if not ret or frame is None:
                frame = 255 * np.ones((480, 640, 3), dtype=np.uint8)
                cv2.putText(frame, 'No Camera Feed!', (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
                
            # Process frame for detection
            try:
                ac_status, ac_boxes = ac_detect(frame, return_boxes=True)
            except Exception as e:
                ac_status, ac_boxes = 'error', []
                cv2.putText(frame, f'AC error: {e}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1)
            try:
                fan_status, fan_boxes = fan_detect(frame, return_boxes=True)
            except Exception as e:
                fan_status, fan_boxes = 'error', []
                cv2.putText(frame, f'Fan error: {e}', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1)
            try:
                human_present, human_boxes = human_detect(frame, return_boxes=True)
            except Exception as e:
                human_present, human_boxes = False, []
                cv2.putText(frame, f'Human error: {e}', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1)
            try:
                mobile_present, mobile_boxes = mobile_detect(frame, return_boxes=True)
            except Exception as e:
                mobile_present, mobile_boxes = False, []
                cv2.putText(frame, f'Mobile error: {e}', (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1)
                
            # Update our global detection status for the API
            detection_results['ac_status'] = ac_status
            detection_results['fan_status'] = fan_status
            detection_results['human_present'] = human_present
            detection_results['mobile_present'] = mobile_present
            
            # Draw boxes for all detections
            for (x1, y1, x2, y2) in ac_boxes:
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                cv2.putText(frame, 'AC', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            for (x1, y1, x2, y2) in fan_boxes:
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)
                cv2.putText(frame, 'Fan', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            for (x1, y1, x2, y2) in human_boxes:
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, 'Human', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            for (x1, y1, x2, y2) in mobile_boxes:
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 255), 2)
                cv2.putText(frame, 'Mobile', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)
            # Draw detection statuses
            cv2.putText(frame, f'AC: {ac_status}', (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
            cv2.putText(frame, f'Fan: {fan_status}', (10, 160), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
            cv2.putText(frame, f'Human: {"Yes" if human_present else "No"}', (10, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
            cv2.putText(frame, f'Mobile: {"Yes" if mobile_present else "No"}', (10, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
            # Notification logic (now 15s)
            now = time.time()
            print(f"[DEBUG] now={now}, last_human_time={last_human_time}, last_notification_time={last_notification_time}, human_present={human_present}, ac_status={ac_status}, fan_status={fan_status}, mobile_present={mobile_present}")
            
            # Get the user email from active_streams
            recipient_email = active_streams.get(thread_id)
            
            if human_present:
                last_human_time = now
                # Reset detection flags since a human is present
                ac_notification_sent = False
                fan_notification_sent = False
                mobile_notification_sent = False
            else:
                # AC notification logic
                if ac_status == 'on':
                    # Set the first detection time if this is a new detection
                    if not ac_notification_sent:
                        ac_first_detected_time = now
                        ac_notification_sent = True
                        print(f"[NOTIFY] AC initially detected in empty room, waiting {NOTIF_INTERVAL} seconds before sending notification")
                    
                    # Only send if AC has been on in empty room for at least 15 seconds AND
                    # we haven't sent a notification in the last 15 seconds
                    if now - ac_first_detected_time >= NOTIF_INTERVAL and recipient_email:
                        if now - last_notification_time >= NOTIF_INTERVAL:
                            print(f"[NOTIFY] Sending email: AC is ON in empty room for 15 sec!")
                            notification_utils.send_email_notification('AC is ON in empty room for 15 sec!', recipient_email)
                            last_notification_time = now
                else:
                    ac_notification_sent = False
                
                # Fan notification logic
                if fan_status == 'on':
                    # Set the first detection time if this is a new detection
                    if not fan_notification_sent:
                        fan_first_detected_time = now
                        fan_notification_sent = True
                        print(f"[NOTIFY] Fan initially detected in empty room, waiting {NOTIF_INTERVAL} seconds before sending notification")
                    
                    # Only send if fan has been on in empty room for at least 15 seconds AND
                    # we haven't sent a notification in the last 15 seconds
                    if now - fan_first_detected_time >= NOTIF_INTERVAL and recipient_email:
                        if now - last_notification_time >= NOTIF_INTERVAL:
                            print(f"[NOTIFY] Sending email: Fan is ON in empty room for 15 sec!")
                            notification_utils.send_email_notification('Fan is ON in empty room for 15 sec!', recipient_email)
                            last_notification_time = now
                else:
                    fan_notification_sent = False
                
                # Mobile phone notification logic
                if mobile_present:
                    # Set the first detection time if this is a new detection
                    if not mobile_notification_sent:
                        last_mobile_detected_time = now
                        mobile_notification_sent = True
                        print(f"[NOTIFY] Mobile phone initially detected, waiting {NOTIF_INTERVAL} seconds before sending notification")
                    
                    # Only send if mobile has been detected for at least 15 seconds AND
                    # we haven't sent a notification in the last 15 seconds
                    if now - last_mobile_detected_time >= NOTIF_INTERVAL and recipient_email:
                        if now - last_notification_time >= NOTIF_INTERVAL:
                            print(f"[NOTIFY] Sending email: Mobile detected in empty room!")
                            notification_utils.send_email_notification('Mobile detected in empty room!', recipient_email)
                            last_notification_time = now
                else:
                    mobile_notification_sent = False
            ret, jpeg = cv2.imencode('.jpg', frame)
            if not ret:
                continue
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        if cap is not None:
            cap.release()
        # Remove the user from active_streams
        if thread_id in active_streams:
            del active_streams[thread_id]

@app.route('/test_cam')
def test_cam():
    import cv2
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()
    if not ret:
        return "No camera feed!"
    return "Camera is working!"

# --- PLACEHOLDER: Detection endpoints and logic will be added here ---

if __name__ == '__main__':
    app.run(debug=True)
