import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import time
from dotenv import load_dotenv

load_dotenv()

# Simple global cache for active SMTP connection to prevent "New Connection" overhead
_cached_server = None
_last_activity = 0

def send_email(to_email, subject, body, attachment=None):
    """
    Sends an email using SMTP.
    Optimized to reuse connections where possible to avoid Gmail rate limits.
    """
    global _cached_server, _last_activity
    
    smtp_server_host = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", 587))
    smtp_username = os.environ.get("SMTP_USERNAME")
    smtp_password = os.environ.get("SMTP_PASSWORD")

    if not smtp_username or not smtp_password:
        print("[ERROR] SMTP credentials not configured.")
        return False

    try:
        msg = MIMEMultipart()
        msg['From'] = f"{os.environ.get('SMTP_FROM_NAME', 'NeuroOps')} <{smtp_username}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))

        # Reuse connection if it was used in the last 60 seconds
        server = None
        if _cached_server:
            if time.time() - _last_activity < 60:
                try:
                    _cached_server.noop() # Check if still connected
                    server = _cached_server
                except:
                    _cached_server = None

        if not server:
            server = smtplib.SMTP(smtp_server_host, smtp_port)
            server.starttls()
            server.login(smtp_username, smtp_password)
            _cached_server = server

        server.sendmail(smtp_username, to_email, msg.as_string())
        _last_activity = time.time()
        
        # Add a small buffer to prevent burst triggers
        time.sleep(0.5) 
        
        return True
        
    except smtplib.SMTPDataError as e:
        if e.smtp_code == 421 or e.smtp_code == 550:
            print(f"[RATE LIMIT] Gmail limit reached: {e}")
        else:
            print(f"[SMTP ERROR] {e}")
        _cached_server = None
        return False
    except Exception as e:
        print(f"[EMAIL FAILED] {e}")
        _cached_server = None
        return False

def close_smtp():
    global _cached_server
    if _cached_server:
        try:
            _cached_server.quit()
        except:
            pass
        _cached_server = None
