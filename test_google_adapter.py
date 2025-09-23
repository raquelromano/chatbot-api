#!/usr/bin/env python3
"""Test script for Google Gemini adapter."""

import asyncio
import logging
import sys
from src.models.google_adapter import GoogleAdapter
from src.models.base import ChatRequest, ChatMessage

# Set up logging to see debug output
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def test_google_adapter():
    """Test the Google adapter with a simple request."""

    # Configure the adapter
    config = {
        "api_key_env": "GOOGLE_API_KEY",
        "model_id": "gemini-2.5-flash"
    }

    adapter = GoogleAdapter(config)

    # Create a test request
    request = ChatRequest(
        model_id="gemini-2.5-flash",
        messages=[
            ChatMessage(role="user", content="Hello! Can you say 'Hello, world!' back to me?")
        ],
        temperature=0.7,
        max_tokens=100
    )

    try:
        print("Testing Google Gemini adapter...")
        print(f"Request: {request}")

        # Test the adapter
        response = await adapter.chat_completion(request)
        print(f"Success! Response: {response}")

    except Exception as e:
        print(f"Error: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()

    finally:
        # Clean up
        await adapter.client.aclose()

if __name__ == "__main__":
    asyncio.run(test_google_adapter())