import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from itsdangerous import URLSafeTimedSerializer

# Email configuration
SENDER_EMAIL = "raosalman504@gmail.com"  # Your Gmail address
APP_PASSWORD = "alix hmrr rghd ffai"  # You'll need to generate an app password for Gmail

# Token configuration
SECRET_KEY = "empty-eye-secret-key-change-this-in-production"
SECURITY_PASSWORD_SALT = "empty-eye-password-reset-salt"

def generate_token(email):
    """Generate a secure token for password reset"""
    serializer = URLSafeTimedSerializer(SECRET_KEY)
    return serializer.dumps(email, salt=SECURITY_PASSWORD_SALT)

def confirm_token(token, expiration=3600):
    """Verify the token is valid and not expired"""
    serializer = URLSafeTimedSerializer(SECRET_KEY)
    try:
        email = serializer.loads(
            token,
            salt=SECURITY_PASSWORD_SALT,
            max_age=expiration
        )
        return email
    except:
        return False

def send_password_reset_email(recipient_email, reset_url):
    """Send password reset email with reset link"""
    message = MIMEMultipart("alternative")
    message["Subject"] = "Empty Eye - Password Reset Request"
    message["From"] = SENDER_EMAIL
    message["To"] = recipient_email
    
    # Create HTML version of the message
    html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eee; border-radius: 5px;">
          <h2 style="color: #333;">Password Reset Request</h2>
          <p>Hello,</p>
          <p>We received a request to reset your password for your Empty Eye account. Click the button below to reset your password:</p>
          <p style="text-align: center;">
            <a href="{reset_url}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; display: inline-block;">Reset Password</a>
          </p>
          <p>If you didn't request a password reset, you can ignore this email.</p>
          <p>This link will expire in 1 hour for security reasons.</p>
          <p>Thank you,<br>Empty Eye Team</p>
        </div>
      </body>
    </html>
    """
    
    # Turn these into plain/html MIMEText objects
    html_part = MIMEText(html, "html")
    
    # Add HTML part to message
    message.attach(html_part)
    
    # Create secure connection with server and send email
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.sendmail(SENDER_EMAIL, recipient_email, message.as_string())
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def send_username_reminder_email(recipient_email, username):
    """Send email with username reminder"""
    message = MIMEMultipart("alternative")
    message["Subject"] = "Empty Eye - Username Reminder"
    message["From"] = SENDER_EMAIL
    message["To"] = recipient_email
    
    # Create HTML version of the message
    html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eee; border-radius: 5px;">
          <h2 style="color: #333;">Username Reminder</h2>
          <p>Hello,</p>
          <p>You requested a reminder of your username for Empty Eye.</p>
          <p>Your username is: <strong>{username}</strong></p>
          <p>You can now log in with this username and your password.</p>
          <p>Thank you,<br>Empty Eye Team</p>
        </div>
      </body>
    </html>
    """
    
    # Turn these into plain/html MIMEText objects
    html_part = MIMEText(html, "html")
    
    # Add HTML part to message
    message.attach(html_part)
    
    # Create secure connection with server and send email
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.sendmail(SENDER_EMAIL, recipient_email, message.as_string())
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
