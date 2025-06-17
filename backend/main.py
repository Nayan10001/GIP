import os
import json
import uuid
import tempfile
import shutil
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import asdict

from fastapi import FastAPI, File, UploadFile, HTTPException, Form, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from PIL import Image
import io

# Import the extractor class (assuming it's saved as extractor.py)
try:
    from extractor import GSTInvoiceExtractor
except ImportError:
    print("Error: extractor.py file not found. Please ensure the GST Invoice Extractor code is saved as 'extractor.py'")
    exit(1)

# Initialize FastAPI app
app = FastAPI(
    title="GST Invoice Data Extractor API",
    description="API for extracting structured data from Indian GST invoices using Gemini AI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models
class TextExtractionRequest(BaseModel):
    invoice_text: str

class ExtractionResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict] = None
    extraction_id: Optional[str] = None
    timestamp: Optional[str] = None

# Global extractor instance
try:
    extractor = GSTInvoiceExtractor()
except Exception as e:
    print(f"Error initializing GST Invoice Extractor: {str(e)}")
    print("Please check your .env file and ensure GEMINI_API_KEY is set")
    extractor = None

# Storage for extracted data (in production, use a database)
extracted_data_store = {}

# Helper Functions
def generate_extraction_id() -> str:
    """Generate unique extraction ID"""
    return f"extract_{uuid.uuid4().hex[:8]}_{int(datetime.now().timestamp())}"

def save_extraction_data(extraction_id: str, data: Dict):
    """Save extracted data to store"""
    extracted_data_store[extraction_id] = {
        "data": data,
        "timestamp": datetime.now().isoformat(),
        "created_at": datetime.now()
    }

def validate_image_file(file: UploadFile) -> bool:
    """Validate uploaded image file"""
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
    file_ext = os.path.splitext(file.filename.lower())[1]
    return file_ext in allowed_extensions

# API Routes

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "GST Invoice Data Extractor API",
        "status": "active",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "extract_from_image": "/extract/image",
            "extract_from_text": "/extract/text",
            "get_extraction": "/extraction/{extraction_id}",
            "list_extractions": "/extractions"
        }
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    gemini_status = "connected" if extractor else "disconnected"
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "gemini_api": gemini_status,
        "total_extractions": len(extracted_data_store)
    }

@app.post("/extract/image", response_model=ExtractionResponse)
async def extract_from_image(file: UploadFile = File(...)):
    """
    Extract GST invoice data from uploaded image file
    
    Supported formats: JPG, JPEG, PNG, BMP, TIFF, WEBP
    """
    if not extractor:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GST Invoice Extractor service is not available. Check API configuration."
        )
    
    # Validate file
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file uploaded"
        )
    
    if not validate_image_file(file):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Supported formats: JPG, JPEG, PNG, BMP, TIFF, WEBP"
        )
    
    # Check file size (max 10MB)
    if file.size and file.size > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size too large. Maximum size is 10MB"
        )
    
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            # Copy uploaded file to temporary file
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name
        
        # Extract data using the extractor
        invoice_data = extractor.extract_from_image(temp_file_path)
        
        # Clean up temporary file
        os.unlink(temp_file_path)
        
        if invoice_data:
            # Generate extraction ID and save data
            extraction_id = generate_extraction_id()
            data_dict = asdict(invoice_data)
            save_extraction_data(extraction_id, data_dict)
            
            return ExtractionResponse(
                success=True,
                message="Invoice data extracted successfully from image",
                data=data_dict,
                extraction_id=extraction_id,
                timestamp=datetime.now().isoformat()
            )
        else:
            return ExtractionResponse(
                success=False,
                message="Failed to extract data from the image. Please ensure it's a valid GST invoice.",
                timestamp=datetime.now().isoformat()
            )
    
    except Exception as e:
        # Clean up temporary file if it exists
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing image: {str(e)}"
        )

@app.post("/extract/text", response_model=ExtractionResponse)
async def extract_from_text(request: TextExtractionRequest):
    """
    Extract GST invoice data from text input
    """
    if not extractor:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GST Invoice Extractor service is not available. Check API configuration."
        )
    
    if not request.invoice_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invoice text cannot be empty"
        )
    
    try:
        # Extract data using the extractor
        invoice_data = extractor.extract_from_text(request.invoice_text)
        
        if invoice_data:
            # Generate extraction ID and save data
            extraction_id = generate_extraction_id()
            data_dict = asdict(invoice_data)
            save_extraction_data(extraction_id, data_dict)
            
            return ExtractionResponse(
                success=True,
                message="Invoice data extracted successfully from text",
                data=data_dict,
                extraction_id=extraction_id,
                timestamp=datetime.now().isoformat()
            )
        else:
            return ExtractionResponse(
                success=False,
                message="Failed to extract data from the text. Please ensure it contains valid GST invoice information.",
                timestamp=datetime.now().isoformat()
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing text: {str(e)}"
        )

@app.get("/extraction/{extraction_id}")
async def get_extraction(extraction_id: str):
    """
    Get previously extracted invoice data by extraction ID
    """
    if extraction_id not in extracted_data_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Extraction ID not found"
        )
    
    extraction_info = extracted_data_store[extraction_id]
    return {
        "extraction_id": extraction_id,
        "data": extraction_info["data"],
        "timestamp": extraction_info["timestamp"]
    }

@app.get("/extractions")
async def list_extractions():
    """
    List all extraction IDs with basic info
    """
    extractions_list = []
    for extraction_id, info in extracted_data_store.items():
        extractions_list.append({
            "extraction_id": extraction_id,
            "timestamp": info["timestamp"],
            "invoice_number": info["data"].get("invoice_details", {}).get("invoice_number", "N/A"),
            "supplier_name": info["data"].get("supplier_details", {}).get("name", "N/A"),
            "total_amount": info["data"].get("total_values", {}).get("total_invoice_value_numbers", 0)
        })
    
    return {
        "total_extractions": len(extractions_list),
        "extractions": sorted(extractions_list, key=lambda x: x["timestamp"], reverse=True)
    }

@app.delete("/extraction/{extraction_id}")
async def delete_extraction(extraction_id: str):
    """
    Delete an extraction by ID
    """
    if extraction_id not in extracted_data_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Extraction ID not found"
        )
    
    del extracted_data_store[extraction_id]
    return {"message": f"Extraction {extraction_id} deleted successfully"}

@app.get("/extraction/{extraction_id}/download")
async def download_extraction(extraction_id: str):
    """
    Download extraction data as JSON file
    """
    if extraction_id not in extracted_data_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Extraction ID not found"
        )
    
    extraction_info = extracted_data_store[extraction_id]
    
    # Create temporary JSON file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
        json.dump(extraction_info["data"], temp_file, indent=2, ensure_ascii=False)
        temp_file_path = temp_file.name
    
    # Return file response
    return FileResponse(
        path=temp_file_path,
        filename=f"gst_invoice_{extraction_id}.json",
        media_type="application/json"
    )

@app.get("/stats")
async def get_stats():
    """
    Get extraction statistics
    """
    total_extractions = len(extracted_data_store)
    
    # Calculate some basic stats
    total_amount = 0
    suppliers = set()
    
    for info in extracted_data_store.values():
        data = info["data"]
        total_amount += data.get("total_values", {}).get("total_invoice_value_numbers", 0)
        supplier_name = data.get("supplier_details", {}).get("name")
        if supplier_name:
            suppliers.add(supplier_name)
    
    return {
        "total_extractions": total_extractions,
        "total_invoice_amount": total_amount,
        "unique_suppliers": len(suppliers),
        "api_status": "active"
    }

# Error Handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"message": "Endpoint not found", "status": "error"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error", "status": "error"}
    )

if __name__ == "__main__":
    import uvicorn
    
    print("Starting GST Invoice Data Extractor API...")
    print("API Documentation will be available at: http://localhost:8000/docs")
    print("Alternative docs at: http://localhost:8000/redoc")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )