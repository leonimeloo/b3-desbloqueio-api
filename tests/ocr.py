from utils.ocr_processor import paddle_read_ocr

def test_paddle_read_ocr():
    with open("FSM2450.pdf", "rb") as f:
        pdf_bytes = f.read()
    
    text = paddle_read_ocr(pdf_bytes)
    
    print("Extracted Text:", text)
    
test_paddle_read_ocr()