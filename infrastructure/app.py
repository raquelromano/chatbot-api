#!/usr/bin/env python3
"""AWS CDK App for Chatbot API deployment."""

import aws_cdk as cdk
from chatbot_stack import ChatbotStack

app = cdk.App()

# Get environment and context
environment = app.node.try_get_context("environment") or "dev"
env = cdk.Environment(
    account=app.node.try_get_context("account"),
    region=app.node.try_get_context("region") or "us-east-1"
)

# Create the stack with environment-specific naming
ChatbotStack(
    app,
    f"ChatbotApiStack-{environment}",
    environment=environment,
    env=env,
    description=f"Serverless chatbot API ({environment}) with Lambda, API Gateway, and Cognito"
)

app.synth()