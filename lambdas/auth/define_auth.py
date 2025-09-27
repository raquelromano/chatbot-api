"""
Lambda function for defining auth challenge in Cognito passwordless flow.
"""
import json


def handler(event, context):
    """
    Define the auth challenge for passwordless authentication.

    This function determines if the authentication flow should issue tokens
    or require a custom challenge (email verification code).
    """
    print(f"DefineAuthChallenge event: {json.dumps(event)}")

    # Check if we already have a successful challenge
    if event['request']['session'] and len(event['request']['session']) > 0:
        for session in event['request']['session']:
            if session.get('challengeName') == 'CUSTOM_CHALLENGE' and session.get('challengeResult') == True:
                event['response']['issueTokens'] = True
                event['response']['failAuthentication'] = False
                return event

    # Start custom challenge for passwordless auth
    event['response']['challengeName'] = 'CUSTOM_CHALLENGE'
    event['response']['issueTokens'] = False
    event['response']['failAuthentication'] = False

    return event