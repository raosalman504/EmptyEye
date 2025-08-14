from db_config import get_db_connection
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl
from email.utils import formataddr

# Email settings - update these with your SMTP details
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "raosalman504@gmail.com"  # Update with your email
SMTP_PASSWORD = "wajq uhir ahfq jgxm"     # Use an app password for Gmail

def send_email_notification(message, recipient_email=None):
    """
    Send an email notification to a user.
    
    Args:
        message (str): The notification message
        recipient_email (str): Email address to send notification to
    """
    if not recipient_email:
        print("[ERROR] No recipient email provided")
        return
        
    try:
        # Store notification in DB
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO notifications (message, timestamp, recipient) VALUES (%s, %s, %s)", 
                     (message, datetime.now(), recipient_email))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"[DB] Notification saved for {recipient_email}")
        
        # Send email
        msg = MIMEMultipart()
        msg['From'] = formataddr(("Empty Eye System", SMTP_USERNAME))
        msg['To'] = recipient_email
        msg['Subject'] = "Empty Eye Alert"
        
        body = f"""
        <html>
        <body>
            <h2>Empty Eye Alert</h2>
            <p>{message}</p>
            <p>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>This is an automated notification from your Empty Eye system.</p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # Create secure context
        context = ssl.create_default_context()
        
        # Connect to server with enhanced security
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.ehlo()  # Identify to the SMTP server
        server.starttls(context=context)  # Secure the connection
        server.ehlo()  # Re-identify over TLS connection
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        
        # Send the email
        server.sendmail(SMTP_USERNAME, recipient_email, msg.as_string())
        server.quit()
        
        print(f"[EMAIL] Notification sent to {recipient_email}")
    except Exception as e:
        print(f"[ERROR] Failed to send email notification: {e}")
