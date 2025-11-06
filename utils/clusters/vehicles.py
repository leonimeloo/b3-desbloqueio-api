import re
from utils.ocr_processor import extract_rotuled_data
from utils.regex_constants import RegexConstants
from utils.field_validators import get_valid_renavam, verify_file_siignatures

def get_vehicle_data(text: str, file_bytes: bytes) -> dict:
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
    renavam = get_valid_renavam(list(dict.fromkeys(re.findall(RegexConstants.VEHICLE_RENAVAM, text))))
    gravame = list(dict.fromkeys(re.findall(RegexConstants.VEHICLE_GRAVAME, text)))
    has_signature = verify_file_siignatures(file_bytes)
    
    people = extract_rotuled_data(text, ["Person"])
        
    return {
        "cpf": cpf,
        "cnpj": cnpj,
        "chassi": chassi,
        "placa": placa,
        "nome_financiado": people,
        "assinatura": has_signature,
        "renavam": renavam,
        "gravame": gravame
    }