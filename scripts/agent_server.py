"""
XHS Signature Agent Server (Pure Algorithm)

A FastAPI-based microservice that provides XHS API signature generation
using the xhshow library. This server acts as a Signature Gateway for
the Rust Core, enabling algorithm-first API interactions.

Usage:
    python scripts/agent_server.py
    
Endpoints:
    POST /sign - Generate signatures for a given request
    GET /health - Health check
"""
import json
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from xhshow import Xhshow

app = FastAPI(
    title="XHS Signature Agent",
    description="Pure Algorithm Signature Gateway for Xiaohongshu API",
    version="1.0.0"
)

# Initialize Xhshow client (singleton)
xhs_client = Xhshow()


class SignRequest(BaseModel):
    """Request model for signature generation"""
    method: str  # GET or POST
    uri: str  # API path, e.g., /api/sns/web/v1/homefeed
    cookies: Dict[str, str]  # Cookie dictionary
    params: Optional[Dict[str, Any]] = None  # Query parameters (for GET)
    payload: Optional[Dict[str, Any]] = None  # Request body (for POST)


class SignResponse(BaseModel):
    """Response model containing generated signatures"""
    success: bool
    x_s: Optional[str] = None
    x_t: Optional[str] = None
    x_s_common: Optional[str] = None
    x_b3_traceid: Optional[str] = None
    x_xray_traceid: Optional[str] = None
    error: Optional[str] = None


@app.post("/sign", response_model=SignResponse)
async def generate_signature(request: SignRequest):
    """
    Generate XHS API signatures for a given request.
    
    This endpoint uses the xhshow library to compute the required
    signature headers (x-s, x-t, x-s-common, etc.) that are needed
    to make authenticated requests to the XHS API.
    
    Note: If the URI contains query parameters (e.g., ?num=20&cursor=),
    they will be automatically extracted and merged with the params field.
    """
    try:
        # Parse URI to extract path and query parameters
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(request.uri)
        uri_path = parsed.path  # Pure path without query string
        
        # Merge query parameters from URI with explicit params
        params = dict(request.params) if request.params else {}
        if parsed.query:
            query_params = parse_qs(parsed.query)
            for key, values in query_params.items():
                # parse_qs returns lists, take first value
                params[key] = values[0] if values else ""
        
        # Debug log
        import logging
        logging.info(f"[Agent] URI: {request.uri} -> path: {uri_path}, params: {params}")
        
        # Generate signatures using xhshow
        result = xhs_client.sign_headers(
            method=request.method.upper(),
            uri=uri_path,  # Use pure path
            cookies=request.cookies,
            params=params if params else None,
            payload=request.payload
        )
        
        return SignResponse(
            success=True,
            x_s=result.get("x-s"),
            x_t=str(result.get("x-t", "")),
            x_s_common=result.get("x-s-common"),
            x_b3_traceid=result.get("x-b3-traceid"),
            x_xray_traceid=result.get("x-xray-traceid")
        )
    except Exception as e:
        return SignResponse(
            success=False,
            error=str(e)
        )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "xhs-signature-agent"}


if __name__ == "__main__":
    print("Starting XHS Signature Agent Server...")
    print("Endpoints:")
    print("  POST /sign - Generate signatures")
    print("  GET /health - Health check")
    print("  GET /docs - OpenAPI documentation")
    uvicorn.run(app, host="127.0.0.1", port=8765)
