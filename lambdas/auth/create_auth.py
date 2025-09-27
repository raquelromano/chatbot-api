"""
Lambda function for creating auth challenge in Cognito passwordless flow.
"""
import json
import boto3
import random
import string
import os


def handler(event, context):
    """
    Create the auth challenge for passwordless authentication.

    This function generates a 6-digit verification code and sends it via email.
    """
    print(f"CreateAuthChallenge event: {json.dumps(event)}")

    if event['request']['challengeName'] == 'CUSTOM_CHALLENGE':
        # Validate email exists in user attributes
        user_email = event.get('request', {}).get('userAttributes', {}).get('email')
        if not user_email:
            raise ValueError("User email not found in request")

        # Generate 6-digit code
        code = ''.join(random.choices(string.digits, k=6))

        # Store code in private challenge parameters
        event['response']['privateChallengeParameters'] = {
            'code': code,
            'email': user_email
        }

        # Send code in public challenge parameters (for client)
        event['response']['publicChallengeParameters'] = {
            'trigger': 'true',
            'email': user_email
        }

        # Send email with code (using SES)
        from utils import send_verification_email, log_auth_event

        try:
            # Use environment variables for configuration (Lambda functions are independent)
            region = os.environ.get('AWS_REGION', 'us-east-1')
            ses = boto3.client('ses', region_name=region)
            from_email = os.environ.get('SES_FROM_EMAIL', 'noreply@chatbot-api.com')

            send_verification_email(ses, from_email, user_email, code)
        except Exception as e:
            log_auth_event("email_send_failed", user_email, {"error": str(e)})

        event['response']['challengeMetadata'] = 'EMAIL_CHALLENGE'

    return event