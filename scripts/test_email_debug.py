
import sys
import os
sys.path.append(os.getcwd())

from app.utils.email import send_email
from dotenv import load_dotenv

load_dotenv()

print("Testing email sending...")
# Use a dummy target, or the sender itself to test
target = os.getenv("EMAIL_USER")
if not target:
    print("EMAIL_USER not found in env.")
else:
    print(f"Sending to {target}...")
    success = send_email(target, "Test Subject", "Test Body")
    print(f"Success: {success}")
