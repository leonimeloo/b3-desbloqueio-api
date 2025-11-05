class RegexConstants:
    CNPJ = r'\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}'
    VEHICLE_CHASSIS = r'[A-HJ-NPR-Z0-9]{17}'
    VEHICLE_PLATE = r'(?:[A-Z]{3}[0-9][A-Z][0-9]{2}|[A-Z]{3}-?[0-9]{4})'  # aceita formato mercosul (BRA2E19) ou antigo com e sem hífen (CMG-3164 e CMG3164)
    CPF = r'\d{3}\.\d{3}\.\d{3}-\d{2}'
    GRAVAME = r'\d{8}'
    RENAVAM = r'\d{9,11}'
    EMAIL = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    ESPECIAL_CHARACTERS_NEAR_NUMBERS = r'(?:(?<=\s)[\-\.\,\/\\](?=\d)|(?<=\d)[\-\.\,\/\\](?=\s))'