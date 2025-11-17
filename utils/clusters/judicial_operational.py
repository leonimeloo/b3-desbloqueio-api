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
    def validate_field(field, extracted, expected, validations, failed_fields):
        '''
        Valida um único campo que está presente em expected_data.
        Retorna True se aprovado, False caso contrário.
        Registra em validations e failed_fields.
        '''
        expected_value = expected[field]
        extracted_value = extracted.get(field)

        is_valid = (extracted_value is not None) and (extracted_value == expected_value)

        validations[field] = {
            'approved': is_valid,
            'expected': expected_value,
            'extracted': extracted_value,
        }

        if not is_valid:
            failed_fields.append(field)

        return is_valid
    
    @staticmethod
    def run_checks(extracted_data: dict, expected_data: dict, file_type: str) -> dict:
        '''Executa as validações relacionadas a veículos.'''
        
        validations = {}
        failed_fields = []
        approved = True #começa com aprovado, se houve alguma falha muda pra false
        
        required_fields = ['chassi', 'placa', 'cpf', 'cnpj']
            
        if file_type == 'termo_responsabilidade':
            required_fields.extend(['agente_financeiro', 'direcionamento_detran'])
        
        missing_extracted_fields = [ f for f in required_fields if f not in extracted_data]
        
        # Campos não identificados pelo "OCR", utilizado para preenchimento da tabela na ServiceNow para visibilidade
        if missing_extracted_fields:
            return {
                'approved': False,
                'failed_fields': missing_extracted_fields,
                'validations': {},
            }
        
        # Faz uma comparação simples (igualdade) de campo a campo obrigatórios para esse tipo de cluster.
        # Implementar fuzzy para campos de texto longo (como nomes).
        for field in required_fields:
            if field in expected_data:
                is_field_valid = JudicialOperationalCluster.validate_field(
                    field, extracted_data, expected_data, validations, failed_fields
                )
                if not is_field_valid:
                    approved = False
            else:
                # Validação para identificar se o chassi não veio no formulário da ServiceNow
                # De qualquer forma, a primeira validação já teria que ser feita no Flow Designer antes de chegar aqui, e preencher na tabela de OCR
                # que o campo não estava presente.
                validations[field] = {
                    'approved': False,
                    'expected': None,
                    'messaged': f'Campo {field} não fornecido no formulário da ServiceNow.',
                    'extracted': extracted_data.get(field, ''),
                }
                failed_fields.append(field)
                approved = False
                
        if file_type in ('auto_mandado_busca', 'termo_entrega_amigavel'):
            is_assinatura_valid = extracted_data.get('assinatura', False) is True
            validations['assinatura'] = {
                'approved': is_assinatura_valid,
                'expected': True,
                'extracted': extracted_data.get('assinatura', False),
            }
            if not is_assinatura_valid:
                failed_fields.append('assinatura')
                approved = False
               
        return {
            'approved': approved,
            'failed_fields': failed_fields,
            'validations': validations
        }