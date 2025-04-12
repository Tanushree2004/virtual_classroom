import hashlib
import hmac
import uuid

SUPER_KEY = "your-super-secret-key"  # Use Django settings for better security

def generate_meeting_id(meeting_name, class_name, host_name):
    raw_string = f"{meeting_name}{class_name}{host_name}{uuid.uuid4().hex}"
    return hashlib.sha256(raw_string.encode()).hexdigest()

def generate_hmac_id(meeting_id, salt, secret):
    """Generates HMAC (Y) for secure meeting links"""
    return hmac.new(salt.encode(), (meeting_id + secret).encode(), hashlib.sha256).hexdigest()
