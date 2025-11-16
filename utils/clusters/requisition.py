import re
from utils.clusters.base_document import BaseDocument

class RequisitionCluster:
    '''Validações e extrações de campos relacionadas a requisições.
    
    O documento é apenas Requerimento.
    '''
    
    @staticmethod
    def extract_fields(text: str) -> dict:
        '''Extrai os campos relacionados a requisições.'''
        
        chassi = BaseDocument.get_chassis(text)
        placa = BaseDocument.get_license_plate(text)
        cpf = BaseDocument.get_cpf(text)
        cnpj = BaseDocument.get_cnpj(text)
        email = BaseDocument.get_email(text)
        renavam = BaseDocument.get_renavam(text)
        pessoas = BaseDocument.extract_rotuled_data(text, ['Person'])
        direcionamento_detran = BaseDocument.detran_directioning_needed(text)
        
        # agente financeiro
        
        return {
            'chassi': chassi,
            'placa': placa,
            'cpf': cpf,
            'cnpj': cnpj,
            'renavam': renavam,
            'email': email,
            'pessoas': pessoas,
            'direcionamento_detran': direcionamento_detran,
        }
    
    def run_checks():
        '''Executa as validações relacionadas a requisições.'''
        return {}