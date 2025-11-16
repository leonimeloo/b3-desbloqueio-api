import logging
from fastapi import APIRouter, UploadFile, File
from sqlalchemy.orm import Session

from utils.ocr_processor import read_pdf, read_ocr
from utils.file_handler import get_file
from utils.clusters.vehicles import get_vehicle_data

pdf_router = APIRouter()

@pdf_router.get("/process")
def process_pdf():
    if request.method == 'GET':
        if not request.headers.get('file-uri'):
            logging.error(f'{"[PROCESS]"} missing "file-uri"')
            return jsonify({
                'message': 'missing filename header'
            }), 400
        if not request.headers.get('file-type'):
            logging.error(f'{"[PROCESS]"} missing "file-type"')
            return jsonify({
                'message': 'missing file-type header'
            }), 400
            
    uri = str(request.headers.get("file-uri"))
    file_type = str(urllib.parse.unquote(request.headers.get("file-type")))
    
    try:
        file = get_file(uri)
        text = read_pdf(file)
        if not text:
            text = read_ocr(file)  # Faz uma leitura um pouco mais avançada e precisa para documentos robustos
            
        return{
            'text': text
        }, 200
    except Exception as e:
        logging.error(f'{"[PROCESS]"} error processing file: {e}')
        return {
            'message': 'error processing file',
            'error': str(e)
        }, 500
        
@pdf_router.post("/validation")
async def validation(file: UploadFile = File(...)):
    file_content = await file.read()
    
    text = read_pdf(file_content)
    if not text:
        text = read_ocr(file_content)
    
    vehicle_data = get_vehicle_data(text)
    vehicle_data['text'] = text
    
    return vehicle_data, 501