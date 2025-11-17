import logging, requests, urllib.parse
from fastapi import APIRouter, UploadFile, File
from sqlalchemy.orm import Session

from utils.ocr_processor import read_pdf, read_ocr
from utils.file_handler import get_file
from utils.clusters.vehicles import get_vehicle_data

pdf_router = APIRouter()
        
@pdf_router.post("/validation")
async def validation(file: UploadFile = File(...)):
    file_content = await file.read()
    
    text = read_pdf(file_content)
    if not text:
        text = read_ocr(file_content)
    
    return {}, 200