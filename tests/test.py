from utils.ocr_processor import read_pdf, read_ocr
from utils.file_handler import get_file
from utils.clusters.vehicles import vehicles

def ocr_file(uri):
    file = get_file(uri)
    text = read_pdf(file)
    if not text:
        text = read_ocr(file)
    
    return text
        
def get_vehicle_data(text):
    return vehicles(text)

if __name__ == "__main__":
    uri = "FSM2450.pdf"
    text = ocr_file(uri)
    vehicle_data = get_vehicle_data(text)
    
    vehicle_data['text'] = text
    
    print(vehicle_data)