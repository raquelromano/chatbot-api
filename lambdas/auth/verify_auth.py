"""
Lambda function for verifying auth challenge in Cognito passwordless flow.
"""
import json


def handler(event, context):
    """
    Verify the auth challenge for passwordless authentication.

    This function compares the provided verification code with the expected code.
    """
    print(f"VerifyAuthChallenge event: {json.dumps(event)}")

    # Get the code from private challenge parameters with validation
    private_params = event.get('request', {}).get('privateChallengeParameters', {})
    expected_code = private_params.get('code', '')
    provided_code = event.get('request', {}).get('challengeAnswer', '')

    if not expected_code:
        print("No expected code found in private challenge parameters")
        event['response']['answerCorrect'] = False
        return event

    if not provided_code:
        print("No challenge answer provided")
        event['response']['answerCorrect'] = False
        return event

    # Verify the code
    event['response']['answerCorrect'] = (expected_code == provided_code)

    return event