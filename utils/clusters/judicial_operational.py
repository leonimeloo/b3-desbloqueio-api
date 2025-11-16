from utils.clusters.base_document import BaseDocument


class JudicialOperationalCluster:
    '''
    Cluster para documentos judiciais e operacionais.
    
    Os documentos são: Auto/mandado de Busca e Apreensão, Termo de Entrega Amigável, Termo de Responsabilidade, Declaração do Financiado.
    '''
    
    # Auto mandado de busca: Nome do financiado
    # Termo: todos + assinatura
    # Termo de responsabilidade: todos + agente financeiro, direcionamento detran
    # Declaração financiado: todos + assinatura
    
    @staticmethod
    def extract_fields(text: str, fyle_type: str, file_bytes: bytes) -> dict:
        '''Extrai os campos relevantes dos documentos judiciais e operacionais.'''
        
        pessoas = BaseDocument.extract_rotuled_data(text, ['Person'])
        chassi = BaseDocument.get_chassis(text)
        placa = BaseDocument.get_license_plate(text)
        cpf = BaseDocument.get_cpf(text)
        cnpj = BaseDocument.get_cnpj(text)
        
        dados_finais = {
            'pessoas': pessoas,
            'chassi': chassi,
            'placa': placa,
            'cpf': cpf,
            'cnpj': cnpj,
        }
        
        if fyle_type == 'termo_responsabilidade':
            agente_financeiro = BaseDocument.extract_financial_agent(text)
            direcionamento_detran = BaseDocument.detran_directioning_needed(text)
            dados_finais.update({
                'agente_financeiro': agente_financeiro, 
                'direcionamento_detran': direcionamento_detran,
            })
        
        if fyle_type in ('auto_mandado_busca', 'termo_entrega_amigavel'):
            assinatura = BaseDocument.verify_signature(file_bytes)
            dados_finais.update({
                'assinatura': assinatura,
            })
        
        return dados_finais
    
    @staticmethod
    def run_checks():
        '''Executa as validações relacionadas a veículos.'''
        return {}