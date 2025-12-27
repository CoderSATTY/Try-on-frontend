import os
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI") 
# New Env Vars for Gmail
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

db = None
users_collection = None

if MONGO_URI:
    try:
        client = MongoClient(MONGO_URI)
        db = client['tryon_app']
        users_collection = db['users']
    except Exception as e:
        print(f"DB Error: {e}")

def generate_code():
    return ''.join(random.choices(string.digits, k=6))

def send_email(to_email, code):
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        return False, "Server Error: Email Not Configured."

    try:
        msg = MIMEMultipart()
        msg['From'] = GMAIL_USER
        msg['To'] = to_email
        msg['Subject'] = "Your Verification Code"

        body = f"<p>Your Verification Code is: <strong>{code}</strong></p>"
        msg.attach(MIMEText(body, 'html'))

        # SMTP Configuration for Gmail (Port 587 is standard for TLS)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        text = msg.as_string()
        server.sendmail(GMAIL_USER, to_email, text)
        server.quit()
        
        return True, "Code sent!"
    except Exception as e:
        print(f"Email Error: {e}") 
        return False, f"Email Failed: {str(e)}"

def register_user(email, name):
    if users_collection is None: 
        return False, "Database Error: Not Connected"
    
    code = generate_code()
    
    email_success, email_msg = send_email(email, code)
    if not email_success:
        return False, email_msg 

    try:
        users_collection.update_one(
            {"email": email},
            {
                "$set": {
                    "verification_code": code, 
                    "last_login": datetime.utcnow(),
                    "name": name
                },
                "$setOnInsert": {"generation_count": 0}
            },
            upsert=True
        )
        return True, "Code sent!"
    except Exception:
        return False, "Database Write Error"

def verify_code(email, code):
    if users_collection is None: return False, "Database Error"
    
    user = users_collection.find_one({"email": email})
    if not user: return False, "User not found."
    
    if str(user.get("verification_code")).strip() == str(code).strip():
        return True, "Verified!"
    return False, "Invalid code."

def check_quota(email):
    if users_collection is None: return True, 3 
    
    user = users_collection.find_one({"email": email})
    if not user: return True, 3 
    
    count = user.get("generation_count", 0)
    if count < 3:
        return True, 3 - count
    return False, 0

def increment_usage(email):
    if users_collection is not None:
        users_collection.update_one(
            {"email": email},
            {"$inc": {"generation_count": 1}}
        )