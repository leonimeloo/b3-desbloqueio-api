class RegexConstants:
    CNPJ = r'\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}'
    VEHICLE_CHASSIS = r'[A-HJ-NPR-Z0-9]{17}'
    VEHICLE_PLATE = r'(?:[A-Z]{3}[0-9][A-Z][0-9]{2}|[A-Z]{3}-?[0-9]{4})'  # aceita formato mercosul (BRA2E19) ou antigo com e sem hífen (CMG-3164 e CMG3164)
    CPF = r'\d{3}\.\d{3}\.\d{3}-\d{2}'
    VEHICLE_GRAVAME = r'\d{8}'
    VEHICLE_RENAVAM = r'\d{9,11}' # alguns renavams no formulário da B3 pode conter 9 ou 11 dígitos, que são zeros à esquerda normalmente
    EMAIL = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    TELEFONE = r'^(?:\+?55\s?)?(?:\(?\d{2}\)?\s?)?(?:9?\d{4})[\s-]?\d{4}$'
    ESPECIAL_CHARACTERS_NEAR_NUMBERS = r'(?:(?<=\s)[\-\.\,\/\\](?=\d)|(?<=\d)[\-\.\,\/\\](?=\s))'