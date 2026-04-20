import time
import uuid
import json
from fastapi import Request
from .logger import logger

async def structured_logging_middleware(request: Request, call_next):
    trace_id = str(uuid.uuid4())
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Calculate latency
    latency_ms = round((time.time() - start_time) * 1000, 2)
    
    # Extract metadata
    store_id = request.path_params.get("id", "N/A")
    endpoint = f"{request.method} {request.url.path}"
    status_code = response.status_code
    
    # Log details
    log_data = {
        "trace_id": trace_id,
        "store_id": store_id,
        "endpoint": endpoint,
        "latency_ms": latency_ms,
        "status_code": status_code,
        "ip": request.client.host
    }
    
    logger.info(f"REQ_LOG: {json.dumps(log_data)}")
    
    # Add trace ID to response headers
    response.headers["X-Trace-ID"] = trace_id
    return response
