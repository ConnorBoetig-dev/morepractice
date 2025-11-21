"""
HEALTH CHECK ROUTES
Production monitoring endpoint

Endpoints:
- GET /health - Application health status
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
from typing import Dict, Any

from app.db.session import get_db


# Create router (no prefix - health check is at root level, not versioned)
router = APIRouter(tags=["health"])


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Returns application health status for monitoring and load balancers"
)
async def health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Health check endpoint for production monitoring

    **No authentication required** - Used by:
    - Load balancers (AWS ELB, Nginx)
    - Monitoring systems (UptimeRobot, Pingdom, DataDog)
    - Kubernetes liveness/readiness probes
    - CI/CD deployment verification

    **Response (200 OK - Healthy)**:
    ```json
    {
        "status": "healthy",
        "timestamp": "2025-11-20T10:30:00.123456",
        "database": "connected",
        "version": "1.0.0"
    }
    ```

    **Response (503 Service Unavailable - Unhealthy)**:
    ```json
    {
        "status": "unhealthy",
        "timestamp": "2025-11-20T10:30:00.123456",
        "database": "disconnected",
        "error": "Database connection failed",
        "version": "1.0.0"
    }
    ```

    **Status Codes**:
    - 200: Service is healthy (all dependencies working)
    - 503: Service is unhealthy (database or critical dependency failed)

    **Performance**:
    - Target response time: < 100ms
    - Database check: Simple SELECT 1 query
    - No heavy operations or complex queries

    **Use Cases**:
    - Load balancer health checks (route traffic to healthy instances)
    - Deployment verification (ensure new version is working)
    - Monitoring alerts (notify on-call when service is down)
    - CI/CD smoke tests (verify deployment succeeded)

    **Example Usage**:
    ```bash
    # Simple health check
    curl http://localhost:8000/health

    # CI/CD deployment verification
    if curl -f http://localhost:8000/health; then
        echo "Deployment successful"
    else
        echo "Deployment failed - rolling back"
        exit 1
    fi

    # Monitoring script
    while true; do
        if ! curl -f http://localhost:8000/health; then
            # Send alert to on-call engineer
            send_alert "API is down!"
        fi
        sleep 60
    done
    ```

    **What This Checks**:
    1. Application is running (FastAPI is responsive)
    2. Database connection is working (can execute queries)
    3. Database is not deadlocked (query completes quickly)

    **What This DOESN'T Check** (keep it fast):
    - External API dependencies (email, payment gateways)
    - Background job queues
    - Cache servers (Redis, Memcached)
    - File storage (S3, CDN)

    For comprehensive health checks, use separate `/health/deep` endpoint
    """
    # Initialize response with current timestamp
    response = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

    # Check database connection
    try:
        # Execute simple query to verify database is responding
        # SELECT 1 is the fastest possible query (no table access)
        db.execute(text("SELECT 1"))
        response["database"] = "connected"

    except Exception as e:
        # Database connection failed - mark as unhealthy
        response["status"] = "unhealthy"
        response["database"] = "disconnected"
        response["error"] = str(e)

        # Return 503 Service Unavailable (tells load balancer to stop routing traffic)
        from fastapi import Response
        return Response(
            content=str(response),
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            media_type="application/json"
        )

    # All checks passed - return 200 OK
    return response
