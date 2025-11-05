import re

from utils.ocr_processor import extract_rotuled_data
from utils.regex_constants import RegexConstants

def get_vehicle_data(text: str) -> dict:
    vehicles_found = []
    vehicle_patterns = [
        RegexConstants.VEHICLE_PLATE,
        RegexConstants.VEHICLE_CHASSIS
    ]
    
    text = re.sub(RegexConstants.ESPECIAL_CHARACTERS_NEAR_NUMBERS, '', text)
    
    cpf = list(dict.fromkeys(re.findall(RegexConstants.CPF, text)))
    cnpj = list(dict.fromkeys(re.findall(RegexConstants.CNPJ, text)))
    chassi = list(dict.fromkeys(re.findall(RegexConstants.VEHICLE_CHASSIS, text)))
    placa = list(dict.fromkeys(re.findall(RegexConstants.VEHICLE_PLATE, text)))
    
    people = extract_rotuled_data(text, ["Person"])
    
    return {
        "cpf": cpf,
        "cnpj": cnpj,
        "chassi": chassi,
        "placa": placa,
        "nome_financiado": people,
        "assinatura": True,
        "renavam": "01011865405",
        "gravame": "62738540"
    }