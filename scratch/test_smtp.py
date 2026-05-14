import os
import sys
from dotenv import load_dotenv

# Add project root and backend to sys.path
current_file = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(current_file))
backend_dir = os.path.join(project_root, 'backend')
sys.path.insert(0, project_root)
sys.path.insert(0, backend_dir)

# Load env from backend
load_dotenv(os.path.join(backend_dir, '.env'))

try:
    from backend.utils.email_service import send_email
    
    recipient = "sushmithatumkur2127@gmail.com" # Using user's email from logs
    subject = "NeuroOps SMTP Test"
    body = "<h1>Success!</h1><p>Your SMTP configuration is now working correctly with the new App Password.</p>"
    
    print(f"Attempting to send test email to {recipient}...")
    success = send_email(recipient, subject, body)
    
    if success:
        print("SUCCESS: Email sent successfully!")
    else:
        print("FAILED: Email failed to send. Check the logs.")
        
except ImportError as e:
    print(f"Import Error: {e}")
except Exception as e:
    print(f"Error: {e}")
