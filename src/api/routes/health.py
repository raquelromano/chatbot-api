"""Health check and status endpoints."""

import time
from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, HTTPException
import structlog

from ...config.settings import settings
from ...models.adapter_factory import get_adapter_factory
from ..models import HealthResponse

logger = structlog.get_logger()
router = APIRouter()


@router.get("/", response_model=HealthResponse)
async def health_check():
    """
    Comprehensive health check endpoint.
    
    Returns the overall health status of the service and all configured models.
    """
    try:
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        # Get adapter factory and check health of all models
        factory = get_adapter_factory()
        
        # Get health status for all adapters
        model_status = await factory.health_check_all()
        
        # Add timestamp to all entries
        overall_healthy = True
        for provider_name, status in model_status.items():
            status["last_checked"] = timestamp
            if status["status"] not in ["available"]:
                overall_healthy = False
        
        # Return health status
        return HealthResponse(
            status="healthy" if overall_healthy else "degraded",
            timestamp=timestamp,
            version="1.0.0",
            models=model_status
        )
        
    except Exception as e:
        logger.error("Health check failed", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Health check failed"
        )


@router.get("/ready")
async def readiness_check():
    """
    Readiness probe for Kubernetes deployments.
    
    Returns 200 if the service is ready to accept traffic.
    """
    try:
        # Basic readiness check - ensure we can access the factory
        factory = get_adapter_factory()
        
        # Check if we have at least one healthy adapter
        health_status = await factory.health_check_all()
        has_healthy_adapter = any(
            status.get("status") == "available" 
            for status in health_status.values()
        )
        
        if not has_healthy_adapter:
            raise HTTPException(
                status_code=503,
                detail="No healthy model adapters available"
            )
        
        return {"status": "ready", "timestamp": datetime.utcnow().isoformat() + "Z"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Readiness check failed", error=str(e))
        raise HTTPException(
            status_code=503,
            detail="Service not ready"
        )


@router.get("/live")
async def liveness_check():
    """
    Liveness probe for Kubernetes deployments.
    
    Returns 200 if the service is alive (basic functionality works).
    """
    try:
        # Basic liveness check - just ensure the service is responding
        return {
            "status": "alive", 
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "uptime_seconds": int(time.time())  # Simple uptime approximation
        }
        
    except Exception as e:
        logger.error("Liveness check failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Service not responding"
        )