"""
Shared utilities for auth Lambda functions.
"""
import json
import boto3
import hashlib
from datetime import datetime


def mask_email(email: str) -> str:
    """Mask email for logging while preserving uniqueness."""
    return hashlib.sha256(email.encode()).hexdigest()[:8]


def log_auth_event(event_type: str, email: str, details: dict = None):
    """Log authentication events in structured format."""
    log_data = {
        "event_type": event_type,
        "email_hash": mask_email(email),
        "timestamp": datetime.utcnow().isoformat(),
        "details": details or {}
    }
    print(json.dumps(log_data))


def format_verification_email(code: str) -> dict:
    """Format verification email content."""
    return {
        'Subject': {'Data': 'Your Chatbot API Verification Code'},
        'Body': {
            'Text': {'Data': f'Your verification code is: {code}\n\nThis code will expire in 5 minutes.'},
            'Html': {'Data': f'<h2>Your verification code is: <strong>{code}</strong></h2><p>This code will expire in 5 minutes.</p>'}
        }
    }


def send_verification_email(ses_client, from_email: str, to_email: str, code: str):
    """Send verification email via SES."""
    message = format_verification_email(code)

    try:
        ses_client.send_email(
            Source=from_email,
            Destination={'ToAddresses': [to_email]},
            Message=message
        )
        log_auth_event("email_sent", to_email, {"code_length": len(code)})
    except Exception as e:
        log_auth_event("email_failed", to_email, {"error": str(e)})
        # For testing - log that email send failed (without exposing email or code)
        print("Email send failed - verification code not delivered")
        raise