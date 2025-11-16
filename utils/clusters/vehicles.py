from base_document import BaseDocument

class VehiclesCluster:
    '''
    Validações e extrações de campos relacionadas a veículos.
    
    Os documentos são: CRLV, CRV, Nota Fiscal e ATPV.
    '''
    
    @staticmethod
    def extract_fields(text: str) -> dict:
        '''
        Extrai os campos relacionados a veículos.
        
        :param text: Texto extraído pelo OCR do documento
        :returns dict: Um dicionário com os campos normalizados.
        '''
        
        chassi = BaseDocument.get_chassis(text)
        placa = BaseDocument.get_license_plate(text)
        cpf = BaseDocument.get_cpf(text)
        cnpj = BaseDocument.get_cnpj(text)
        # nome financiado, data e pessoas
        
        return {}
    
    @staticmethod
    def run_checks():
        '''Executa as validações relacionadas a veículos.'''
        return {}