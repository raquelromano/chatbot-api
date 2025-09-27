#!/usr/bin/env python3
"""
Simple test script to verify API endpoints work.

This script tests the API without requiring external model services.
"""

import asyncio
import httpx
import json
import time
from typing import Dict, Any


async def test_api_endpoints():
    """Test the main API endpoints."""
    
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        print("🧪 Testing Chatbot Wrapper Demo API")
        print("=" * 50)
        
        # Test 1: Root endpoint
        print("\n1. Testing root endpoint...")
        try:
            response = await client.get(f"{base_url}/")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   App name: {data.get('name')}")
                print(f"   Version: {data.get('version')}")
                print("   ✅ Root endpoint working")
            else:
                print("   ❌ Root endpoint failed")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 2: Health check
        print("\n2. Testing health check...")
        try:
            response = await client.get(f"{base_url}/health/")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Health status: {data.get('status')}")
                print(f"   Models available: {len(data.get('models', {}))}")
                print("   ✅ Health check working")
            else:
                print("   ❌ Health check failed")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 3: Liveness probe
        print("\n3. Testing liveness probe...")
        try:
            response = await client.get(f"{base_url}/health/live")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ Liveness probe working")
            else:
                print("   ❌ Liveness probe failed")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 4: Readiness probe
        print("\n4. Testing readiness probe...")
        try:
            response = await client.get(f"{base_url}/health/ready")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ Readiness probe working")
            elif response.status_code == 503:
                print("   ⚠️  Service not ready (expected without model services)")
            else:
                print("   ❌ Readiness probe failed")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 5: Models list
        print("\n5. Testing models list...")
        enabled_models = []
        try:
            response = await client.get(f"{base_url}/v1/models")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                models = data.get('data', [])
                enabled_models = models  # API only returns enabled models

                print(f"   Available models: {len(enabled_models)}")
                print(f"\n   🟢 ENABLED models (ready for chat completions):")
                for model in enabled_models:
                    print(f"     ✅ {model.get('id')} ({model.get('provider')})")

                if len(enabled_models) == 0:
                    print("     ⚠️  No models enabled - need API keys or local services")

                print("\n   ✅ Models list working")
            else:
                print("   ❌ Models list failed")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 6: Chat completion tests
        print("\n6. Testing chat completions...")

        if enabled_models:
            # Note: Using free tier of Gemini models. Gemini 2.5 Pro uses extensive
            # "thoughts tokens" for internal reasoning (50-99 tokens) which exhausts
            # the small test token limit, so we skip it to avoid meaningless empty responses.
            # Gemini 2.5 Flash is more efficient and works with small token limits.

            # Test each enabled model (skip Gemini Pro due to free tier token limits)
            for i, model in enumerate(enabled_models, 1):
                model_id = model['id']
                provider = model['provider']

                # Skip Gemini Pro - uses too many internal reasoning tokens for small tests
                if model_id == "gemini-2.5-pro":
                    print(f"\n   6.{i} Skipping {model_id} ({provider}) - requires higher token limits due to internal reasoning")
                    continue

                print(f"\n   6.{i} Testing {model_id} ({provider})...")

                try:
                    chat_request = {
                        "messages": [{"role": "user", "content": "Say 'Hello from API test!' in exactly those words."}],
                        "model_id": model_id,
                        "max_tokens": 50,
                        "temperature": 0.1,
                        "stream": False
                    }

                    response = await client.post(
                        f"{base_url}/v1/chat/completions",
                        json=chat_request,
                        timeout=30.0
                    )
                    print(f"      Status: {response.status_code}")

                    if response.status_code == 200:
                        data = response.json()
                        content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
                        print(f"      ✅ SUCCESS - Generated response: '{content[:80]}{'...' if len(content) > 80 else ''}'")
                        if data.get('usage'):
                            usage = data['usage']
                            print(f"      Tokens used: {usage.get('total_tokens', 0)} total")
                    elif response.status_code == 500:
                        error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                        print(f"      ❌ FAILED - Server error: {error_data.get('detail', 'Unknown error')}")
                    elif response.status_code == 404:
                        print("      ❌ FAILED - Model not found")
                    else:
                        print(f"      ❌ FAILED - Unexpected status: {response.status_code}")

                except Exception as e:
                    print(f"      ❌ FAILED - Error: {e}")
        else:
            print("\n   No enabled models found - add API keys to enable models")
            print("   Example: Set GOOGLE_API_KEY environment variable for Gemini models")
        
        print("\n" + "=" * 50)
        print("🎉 API testing complete!")
        print(f"\nSummary:")
        print(f"- 🟢 Enabled models tested: {len(enabled_models)}")
        if enabled_models:
            print("- Only enabled models are shown and tested")
            print("- Enabled models should generate actual responses")
        else:
            print("- No models enabled - configure API keys to enable models")
            print("- Disabled models (OpenAI, Anthropic, local vLLM) need credentials")


async def main():
    """Main test function."""
    print("Starting API test...")
    print("Make sure the server is running with: python run_server.py")
    print("Waiting 3 seconds for server to be ready...")
    await asyncio.sleep(3)
    
    try:
        await test_api_endpoints()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("Make sure the server is running: python run_server.py")


if __name__ == "__main__":
    asyncio.run(main())