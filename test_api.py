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
        try:
            response = await client.get(f"{base_url}/v1/models")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                models = data.get('data', [])
                print(f"   Models configured: {len(models)}")
                for model in models[:3]:  # Show first 3 models
                    print(f"     - {model.get('id')} ({model.get('provider')})")
                print("   ✅ Models list working")
            else:
                print("   ❌ Models list failed")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 6: Chat completion (will likely fail without model services)
        print("\n6. Testing chat completion...")
        try:
            chat_request = {
                "messages": [{"role": "user", "content": "Hello, this is a test"}],
                "model_id": "gpt-3.5-turbo",
                "max_tokens": 10,
                "temperature": 0.7,
                "stream": False
            }
            
            response = await client.post(
                f"{base_url}/v1/chat/completions",
                json=chat_request,
                timeout=10.0
            )
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Model used: {data.get('model')}")
                print("   ✅ Chat completion working")
            elif response.status_code == 404:
                print("   ⚠️  Model not found (expected without model services)")
            elif response.status_code == 500:
                print("   ⚠️  Server error (expected without model services)")
            else:
                print(f"   ❌ Unexpected status: {response.status_code}")
                
        except Exception as e:
            print(f"   ⚠️  Error (expected without model services): {e}")
        
        print("\n" + "=" * 50)
        print("🎉 API testing complete!")
        print("\nNote: Some endpoints may show warnings/errors without")
        print("actual model services (OpenAI API key, vLLM server, etc.)")
        print("This is expected behavior.")


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