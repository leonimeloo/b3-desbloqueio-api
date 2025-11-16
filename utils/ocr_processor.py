import io, os, logging
import numpy as np
from typing import Optional
from pdf2image import convert_from_bytes
from paddleocr import PaddleOCR
from pypdf import PdfReader

# from gliner import GLiNER

openai.api_key = os.getenv("OPENAI_API_KEY")

def read_pdf(read_file: bytes) -> Optional[str]:
    '''
    Extrai o texto selecionável de um arquivo PDF.
    '''
    with io.BytesIO(read_file) as pdf_file:
        try:
            text = str()
            pdf = PdfReader(pdf_file)
            n_pages = len(pdf.pages)
            count = 0
            while count < n_pages:
                page_object = pdf.pages[count]
                text += page_object.extract_text()
                count += 1 
            return text
            
        except Exception as e: 
            logging.error(f'Erro: {e}')
            return None
        
def read_ocr(read_file: bytes) -> Optional[str]:
    images = convert_from_bytes(read_file)

    ocr = PaddleOCR(use_doc_orientation_classify=False,use_doc_unwarping=False,use_textline_orientation=False)

    final_text = str()
    for img in images:
        img_np = np.array(img)
        result = ocr.predict(img_np)
        final_text += '\n'.join(result[0]['rec_texts'])

    return final_text
        
# def tesseract_read_ocr(read_file: bytes) -> Optional[str]:
#     '''
#     Extrai o texto de um arquivo PDF utilizando OCR com Tesseract (Desativado).
#     '''
#     images = convert_from_bytes(read_file)

#     final_text = []
#     for img in images:
#         text = pytesseract.image_to_string(img, lang='por')
#         final_text.append(text)

#     return '\n'.join(final_text)