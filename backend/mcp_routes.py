"""
FastAPI routes for MCP Schedule Converter integration
Add this to your existing FastAPI application
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import sys
import os
import json
import tempfile

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_integration import MCPScheduleConverterContext, MCPScheduleConverter

# Create router
router = APIRouter(prefix="/api/mcp", tags=["MCP Tools"])

# Global converter instance (reused for performance)
converter_instance = None


class ConversionRequest(BaseModel):
    """Request model for schedule conversion"""
    content: str
    file_type: str = "csv"
    target_format: str = "CDISC_SDTM"
    organization_id: Optional[str] = None


class ConversionResponse(BaseModel):
    """Response model for schedule conversion"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    confidence: Optional[float] = None
    llm_mode: Optional[str] = None
    error: Optional[str] = None


def get_converter():
    """Get or create the MCP converter instance"""
    global converter_instance
    if converter_instance is None or not converter_instance.initialized:
        converter_instance = MCPScheduleConverter()
        if not converter_instance.start():
            raise HTTPException(status_code=500, detail="Failed to start MCP server")
    return converter_instance


@router.post("/convert", response_model=ConversionResponse)
async def convert_schedule(request: ConversionRequest):
    """
    Convert a clinical trial schedule to standard format using MCP

    - **content**: The schedule content (CSV, JSON, etc.)
    - **file_type**: Type of content (csv, json, text)
    - **target_format**: Target format (CDISC_SDTM, FHIR_R4, OMOP_CDM)
    - **organization_id**: Optional organization ID for caching
    """
    try:
        converter = get_converter()

        result = converter.convert_schedule(
            file_content=request.content,
            file_type=request.file_type,
            target_format=request.target_format,
            organization_id=request.organization_id
        )

        if result.get("success"):
            return ConversionResponse(
                success=True,
                data=result.get("data"),
                confidence=result.get("confidence"),
                llm_mode=result.get("llm_mode")
            )
        else:
            return ConversionResponse(
                success=False,
                error=result.get("error", "Conversion failed")
            )

    except Exception as e:
        return ConversionResponse(
            success=False,
            error=str(e)
        )


@router.post("/upload-and-convert", response_model=ConversionResponse)
async def upload_and_convert(
    file: UploadFile = File(...),
    target_format: str = "CDISC_SDTM",
    organization_id: Optional[str] = None
):
    """
    Upload a file and convert it to standard format

    - **file**: The schedule file to upload
    - **target_format**: Target format (CDISC_SDTM, FHIR_R4, OMOP_CDM)
    - **organization_id**: Optional organization ID for caching
    """
    try:
        # Read uploaded file
        content = await file.read()
        content_str = content.decode('utf-8')

        # Determine file type from extension
        file_type = "csv"
        if file.filename.endswith('.json'):
            file_type = "json"
        elif file.filename.endswith('.txt'):
            file_type = "text"

        converter = get_converter()

        result = converter.convert_schedule(
            file_content=content_str,
            file_type=file_type,
            target_format=target_format,
            organization_id=organization_id
        )

        if result.get("success"):
            return ConversionResponse(
                success=True,
                data=result.get("data"),
                confidence=result.get("confidence"),
                llm_mode=result.get("llm_mode")
            )
        else:
            return ConversionResponse(
                success=False,
                error=result.get("error", "Conversion failed")
            )

    except Exception as e:
        return ConversionResponse(
            success=False,
            error=str(e)
        )


@router.post("/convert-and-optimize")
async def convert_and_optimize(request: ConversionRequest):
    """
    Convert schedule and provide optimization recommendations

    This endpoint:
    1. Converts the schedule to CDISC SDTM
    2. Also converts to FHIR for interoperability
    3. Provides optimization recommendations
    """
    try:
        converter = get_converter()

        # Convert to CDISC SDTM
        sdtm_result = converter.convert_schedule(
            file_content=request.content,
            file_type=request.file_type,
            target_format="CDISC_SDTM",
            organization_id=request.organization_id
        )

        if not sdtm_result.get("success"):
            return {
                "success": False,
                "error": sdtm_result.get("error", "SDTM conversion failed")
            }

        # Convert to FHIR
        fhir_result = converter.convert_schedule(
            file_content=request.content,
            file_type=request.file_type,
            target_format="FHIR_R4",
            organization_id=request.organization_id
        )

        # Get optimization recommendations
        optimized = converter.optimize_schedule(sdtm_result['data'])

        return {
            "success": True,
            "cdisc_sdtm": sdtm_result.get("data"),
            "fhir": fhir_result.get("data") if fhir_result.get("success") else None,
            "optimization": optimized,
            "confidence": sdtm_result.get("confidence"),
            "metadata": {
                "llm_mode": sdtm_result.get("llm_mode"),
                "arbitration_used": sdtm_result.get("arbitration_used", False)
            }
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/status")
async def get_mcp_status():
    """Check if the MCP server is running and available"""
    global converter_instance

    if converter_instance and converter_instance.initialized:
        return {
            "status": "running",
            "server_path": str(converter_instance.server_script),
            "initialized": True
        }
    else:
        return {
            "status": "not_running",
            "initialized": False
        }


@router.post("/restart")
async def restart_mcp_server():
    """Restart the MCP server"""
    global converter_instance

    try:
        if converter_instance:
            converter_instance.stop()

        converter_instance = MCPScheduleConverter()
        if converter_instance.start():
            return {"success": True, "message": "MCP server restarted"}
        else:
            return {"success": False, "message": "Failed to restart MCP server"}

    except Exception as e:
        return {"success": False, "error": str(e)}


# Cleanup on shutdown
def shutdown_mcp():
    """Shutdown the MCP server gracefully"""
    global converter_instance
    if converter_instance:
        converter_instance.stop()
        converter_instance = None


# To integrate with your existing FastAPI app:
#
# from fastapi import FastAPI
# from backend.mcp_routes import router as mcp_router, shutdown_mcp
#
# app = FastAPI()
# app.include_router(mcp_router)
#
# @app.on_event("shutdown")
# async def shutdown_event():
#     shutdown_mcp()