import re
from gliner import GLiNER
from transformers import pipeline

from utils.regex_constants import RegexConstants
from utils.field_validators import verify_file_signatures
from utils.ocr_processor import extract_rotuled_data

class BaseDocument:
    '''Classe base para documentos, fornecendo funcionalidades compartilhadas entre os clusters.'''
    
    _qa_model = pipeline("question-answering", model="deepset/xlm-roberta-large-squad2")
    _ner_model = GLiNER.from_pretrained("urchade/gliner_base")
    
    @staticmethod
    def get_cpf(text: str) -> list:
        if not text:
            raise Exception("Texto não pode ser vazio")
        
        cpf = list(dict.fromkeys(re.findall(RegexConstants.CPF, text)))
        
        return cpf
    
    @staticmethod
    def get_cnpj(text: str) -> list:
        if not text:
            raise Exception("Texto não pode ser vazio")
        
        cpf = list(dict.fromkeys(re.findall(RegexConstants.CPF, text)))
        
        return cpf
    
    @staticmethod
    def get_license_plate(text: str) -> list:
        if not text:
            raise Exception("Texto não pode ser vazio")
        
        vehicle_plate = list(dict.fromkeys(re.findall(RegexConstants.VEHICLE_PLATE, text)))
        
        return vehicle_plate
    
    @staticmethod
    def get_renavam(text: str) -> list:
        if not text:
            raise Exception("Texto não pode ser vazio")
        
        renavam = list(dict.fromkeys(re.findall(RegexConstants.VEHICLE_RENAVAM, text)))
        
        return renavam
    
    @staticmethod
    def get_chassis(text: str) -> list:
        if not text:
            raise Exception("Texto não pode ser vazio")
        
        chassis = list(dict.fromkeys(re.findall(RegexConstants.VEHICLE_CHASSIS, text)))
        
        return chassis
    
    @staticmethod
    def get_email(text: str) -> list:
        if not text:
            raise Exception("Texto não pode ser vazio")
        
        email = list(dict.fromkeys(re.findall(RegexConstants.EMAIL, text)))
        
        return email
    
    @staticmethod
    def get_phone_number(text: str) -> list:
        if not text:
            raise Exception("Texto não pode ser vazio")
        
        phone_number = list(dict.fromkeys(re.findall(RegexConstants.TELEFONE, text)))
        
        return phone_number
    
    @staticmethod
    def verify_signature(file_bytes: bytes) -> bool:
        if not file_bytes:
            raise Exception("Bytes do arquivo não podem ser vazios")
        
        return verify_file_signatures(file_bytes)
    
    @staticmethod
    def extract_rotuled_data(text: str, labels: list[str]) -> list[str]:
        '''Extrai dados rotulados do texto usando um modelo de NER.'''
        if not text:
            raise Exception("Texto não pode ser vazio")
        if len(labels) <= 0:
            raise Exception("Labels não podem ser vazias")
        
        entities = BaseDocument._ner_model.predict_entities(text, labels)
        people_set = set()

        people = []

        for item in entities:
            text = item["text"]
            label = item["label"]
            text_lower = text.lower()

            if label == "Person" and text_lower not in people_set:
                people_set.add(text_lower)
                people.append(text)

        return people
    
    @staticmethod
    def document_question_answering(document_text: str, questions: dict[str, str]) -> dict[str, str]:
        '''Responde a uma pergunta com base no texto do documento fornecido.'''
        if not document_text:
            raise Exception("Texto do documento não pode ser vazio")
        if not questions:
            raise Exception("Perguntas não podem ser vazias")
        
        answers = {}
        
        for label, question in questions.items():
            result = BaseDocument._qa_model(question=question, context=document_text)
            answers[label] = result.get("answer", None)
        
        return answers
    
    @staticmethod
    def detran_directioning_needed(text: str) -> bool:
        '''Verifica se está direcionado ao Detran'''
        patterns = [
            r'ao\s+detran[/\s]*(?:de\s+)?(?:sp|são\s+paulo)?',
            r'ao\s+departamento\s+estadual\s+de\s+trânsito(?:\s+de\s+são\s+paulo)?',
            r'ao\s+departamento\s+estadual\s+de\s+são\s+paulo',
            r'ao\s+dept[oº]?\s+estadual\s+de\s+trânsito',
        ]
        
        text_lower = text.lower()
        mentions = []
        
        for pattern in patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                mentions.append(match.group())
        
        return len(list(set(mentions))) > 0