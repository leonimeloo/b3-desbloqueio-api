import base64, os, json, re, tempfile, openai
from io import BytesIO
from const import ReConstants
from typing import List, Tuple
from pdf2image import convert_from_bytes
from google.cloud import vision
from google.cloud.vision_v1 import types
from google.oauth2 import service_account

from main import credenciais, logging

# Início Validação Renavam
def get_factor(num):
    digits = [2, 3, 4, 5, 6, 7, 8, 9]

    if num >= len(digits):
        index = num % len(digits)
    else:
        index = num

    return digits[index]


def get_reversed_digits(renavam):
    renavam = str(renavam)[0:(len(renavam) - 1)]
    digits = []
    for char in renavam:
        digits += [int(char)]

    digits.reverse()

    return digits

def get_sum(digits):
    sum_numbers = 0
    for i in range(0, len(digits)):
        sum_numbers += digits[i] * get_factor(i)
    return sum_numbers


def get_verificator(sum_numbers):
    value = 11 - (sum_numbers % 11)
    if value >= 10:
        return 0
    return value

def get_verificator_digit(renavam):
    return int(str(renavam)[-1])

def validate_renavam(renavam):
    if len(renavam) != 11:
        renavam = str(renavam).ljust(11, '0')

    if not re.match(r'^\d{11}$', renavam):
        return False

    digits = get_reversed_digits(renavam)
    verifier = get_verificator_digit(renavam)

    sum_numbers = get_sum(digits)
    calculated_verifier = get_verificator(sum_numbers)

    return calculated_verifier == verifier

def normalize_renavam(renavam: str):
    if len(renavam) != 11:
        renavam = str(renavam).rjust(11, '0')
    return renavam

def get_valid_renavam(renavam: List[str]) -> List[str]:
    """
    Recebe uma lista de renavam e retorna uma lista com os renavam válidos
    """
    valid_renavam = []
    if len(renavam) > 0:
        for item in renavam:
            normalized_renavam = normalize_renavam(item)
            if validate_renavam(normalized_renavam):
                valid_renavam.append(normalized_renavam)
    return valid_renavam

# Término Validação Renavam

def validate_cnpj(cnpj):
    '''
    Valida se um CNPJ é válido com base em seus dígitos verificadores.
    '''
    b = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    c = re.sub(r'\D', '', str(cnpj))

    if len(c) != 14:
        return False

    if re.fullmatch(r'0{14}', c):
        return False

    n = 0
    i = 0
    while i < 12:
        i += 1
        n += int(c[i - 1]) * b[i]
    if int(c[12]) != (0 if n % 11 < 2 else 11 - (n % 11)):
        return False

    n = 0
    i = 0
    while i <= 12:
        n += int(c[i]) * b[i]
        i += 1
    if int(c[13]) != (0 if n % 11 < 2 else 11 - (n % 11)):
        return False

    return True

def validate_cpf(cpf):
    '''
    Valida se um CPF é válido com base em seus dígitos verificadores.
    '''
    if not isinstance(cpf,str):
        return False

    cpf = re.sub("[^0-9]",'',cpf)
    
    if cpf=='00000000000' or cpf=='11111111111' or cpf=='22222222222' or cpf=='33333333333' or cpf=='44444444444' or cpf=='55555555555' or cpf=='66666666666' or cpf=='77777777777' or cpf=='88888888888' or cpf=='99999999999':
        return False

    if len(cpf) != 11:
        return False

    sum = 0
    weight = 10

    for n in range(9):
        sum = sum + int(cpf[n]) * weight

        weight = weight - 1

    verifyingDigit = 11 -  sum % 11

    if verifyingDigit > 9 :
        firstVerifyingDigit = 0
    else:
        firstVerifyingDigit = verifyingDigit

    sum = 0
    weight = 11
    for n in range(10):
        sum = sum + int(cpf[n]) * weight

        weight = weight - 1

    verifyingDigit = 11 -  sum % 11

    if verifyingDigit > 9 :
        secondVerifyingDigit = 0
    else:
        secondVerifyingDigit = verifyingDigit

    if cpf[-2:] == "%s%s" % (firstVerifyingDigit,secondVerifyingDigit):
        return True
    return False

def verify_digital_signature(file_bytes):
    '''
    Verifica se há assinatura digital em um arquivo PDF.
    '''
    try:
        with tempfile.NamedTemporaryFile(delete=True, suffix=".pdf") as tmp_file:
            tmp_file.write(file_bytes)
            tmp_file.flush()
            reader = PdfReader(tmp_file.name)
            fields = reader.get_fields()
            for field_name, field_value in fields.items():
                if field_value.field_type == '/Sig':
                    return True
            return False
    except Exception as e:
        print(f"Erro na leitura do PDF sig: {e}")
        return False
    
def verify_handwritten_signature(file):
    '''
    Verifica se há assinatura manuscrita em uma imagem usando a API do Google Vision.
    '''
    img = convert_from_bytes(file)[-1]
    
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    
    client = vision.ImageAnnotatorClient(credentials=credenciais)
    
    img_bytes = buffer.read()

    image = vision.Image(content=img_bytes)

    response = client.document_text_detection(image=image)

    text = response.full_text_annotation.text.strip()
    
    return bool(text)

def verify_file_signatures(file_bytes):
    '''
    Verifica se há assinatura digital ou manuscrita em um arquivo.
    ''' 
    return verify_digital_signature(file_bytes) or verify_handwritten_signature(file_bytes)