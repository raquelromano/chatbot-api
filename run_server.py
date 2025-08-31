#!/usr/bin/env python3
"""
Simple script to run the FastAPI server.

Usage:
    python run_server.py

This script will:
1. Import the FastAPI app
2. Start the server using uvicorn
3. Handle graceful shutdown
"""

import sys
import asyncio
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    import uvicorn
    from src.api.main import app
    from src.config.settings import settings
    from src.models.adapter_factory import close_adapter_factory
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("\nPlease install dependencies first:")
    print("  pip install -r requirements.txt")
    print("  # or")
    print("  uv pip install -r requirements.txt")
    sys.exit(1)


async def shutdown_handler():
    """Clean shutdown handler."""
    print("\nShutting down gracefully...")
    await close_adapter_factory()
    print("Shutdown complete.")


if __name__ == "__main__":
    try:
        print(f"Starting {settings.app_name}")
        print(f"Server will be available at: http://{settings.host}:{settings.port}")
        print(f"API docs at: http://{settings.host}:{settings.port}/docs")
        print("\nPress Ctrl+C to stop the server")
        
        uvicorn.run(
            "src.api.main:app",
            host=settings.host,
            port=settings.port,
            reload=settings.debug,
            log_level=settings.log_level.lower(),
        )
        
    except KeyboardInterrupt:
        print("\nReceived interrupt signal")
        asyncio.run(shutdown_handler())
    except Exception as e:
        print(f"Server error: {e}")
        asyncio.run(shutdown_handler())
        sys.exit(1)