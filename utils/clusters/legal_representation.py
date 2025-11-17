import json

from configs import openai
from utils.clusters.base_document import BaseDocument

class LegalRepresentationCluster:
    '''
    Validações e extrações de campos relacionadas a veículos.
    
    Os documentos de veículos incluem: Procuração e Contrato Social
    '''
    
    @staticmethod
    def extract_financial_advisor(text: str) -> dict:
        '''
        Extrai o nome do agente financeiro do texto.
        
        :param text: Texto extraído pelo OCR do documento
        :returns dict: Dados do agente financeiro
        '''
        structure = {
            "name": "extrair_data",
            "description": "Identifique a data de expedição da procuração, o texto de vencimento, o nome e o CNPJ do agente financeiro calculando a data de validade.",
            "parameters": {
                "type": "object",
                "properties": {
                    "data_expedicao": {
                        "type": "string",
                        "description": "Data de expedição da procuração no formato AA/MM/YYYY. Normalmente vem no início do texto."
                    },
                    "data_validade": {
                        "type": "string",
                        "description": "Data de validade da procuração no formato AA/MM/YYYY"
                    },
                    "agente_financeiro": {
                        "type": "string",
                        "description": "Nome do agente financeiro mencionado no texto."
                    },
                    "cnpj_agente": {
                        "type": "string",
                        "description": "CNPJ do agente financeiro mencionado no texto."
                    }
                },
                "required": ["data_expedicao", "data_validade", "agente_financeiro", "cnpj_agente"],
                "additionalProperties": False
            }
        }

        system_prompt = (
            "Procure no texto a data de expedição da procuração e o texto que fala sobre a validade. Normalmente os textos sobre a validade vem escrito algo tipo 'A presente procuração terá validade de X ano a contar desta data'. Já os textos sobre a data de expedição normalmente vem no início do documento, exemplo: 'Aos dez dias do mês de janeiro de dois mil e vinte'."
            "Sempre que as datas não estiverem explícitas, tente inferir a data de expedição a partir do texto escrito por extenso. Calcule a data de validade se for baseada em um período de tempo."
            "Retorne ambas as datas no formato AA/MM/YYYY."
            "Além disso, identifique o nome e o CNPJ do agente financeiro mencionado no texto."
        )

        user_prompt = f"Texto:\n{text}"

        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            functions=[structure],
            function_call={"name": "extrair_data"},
            temperature=0.0
        )

        arguments = response['choices'][0]['message']['function_call']['arguments']

        try:
            structured_data = json.loads(arguments)
            return structured_data
        except Exception:
            return {}
    
    @staticmethod
    def extract_fields(text: str, file_bytes: str) -> dict:
        '''
        Extrai os campos relacionados a veículos.
        
        :param text: Texto extraído pelo OCR do documento
        :param file_bytes: Bytes do arquivo do documento
        :returns dict: Um dicionário com os campos normalizados.
        '''
        
        cnpj = BaseDocument.get_cnpj(text)
        assinatura = BaseDocument.verify_signature(file_bytes)
        dados_agente_financeiro = LegalRepresentationCluster.extract_financial_advisor(text)
        agente_financeiro = dados_agente_financeiro.get("agente_financeiro", "")
        cnpj_agente = dados_agente_financeiro.get("cnpj_agente", "")
        data_expedicao = dados_agente_financeiro.get("data_expedicao", "")
        data_validade = dados_agente_financeiro.get("data_validade", "")
        
        # pessoas
        
        return {
            "agente_financeiro": agente_financeiro,
            "cnpj_agente": cnpj_agente,
            "assinatura": assinatura,
            "cnpj": cnpj,
            "datas": {
                "data_expedicao": data_expedicao,
                "data_validade": data_validade
            }
        }
        
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
    
    def run_checks(extracted_data: dict, expected_data: dict) -> dict:
        '''Executa as validações relacionadas a veículos.'''
        
        validations = {}
        failed_fields = []
        approved = True #começa com aprovado, se houve alguma falha muda pra false
        
        # Trocar pela função validate_field para os campos simples
        
        if 'cnpj' in expected_data:
            is_cnpj_valid = expected_data.get('cnpj') in extracted_data.get('cnpj', [])
            validations['cnpj'] = {
                'approved': is_cnpj_valid,
                'expected': expected_data.get('cnpj', ''),
                'extracted': extracted_data.get('cnpj', ''),
            }
            if not is_cnpj_valid:
                failed_fields.append('cnpj')
                approved = False

        if 'cnpj_agente' in expected_data:
            is_cnpj_agente_valid = extracted_data.get('cnpj_agente') == expected_data.get('cnpj_agente')
            validations['cnpj_agente'] = {
                'approved': is_cnpj_agente_valid,
                'expected': expected_data.get('cnpj_agente', ''),
                'extracted': extracted_data.get('cnpj_agente', ''),
            }
            if not is_cnpj_agente_valid:
                failed_fields.append('cnpj_agente')
                approved = False
                
        if 'data_validade' in expected_data:
            is_data_validade_valid = extracted_data.get('datas', {}).get('data_validade') == expected_data.get('data_validade')
            validations['data_validade'] = {
                'approved': is_data_validade_valid,
                'expected': expected_data.get('data_validade', ''),
                'extracted': extracted_data.get('datas', {}).get('data_validade', ''),
            }
            if not is_data_validade_valid:
                failed_fields.append('data_validade')
                approved = False
                
        if 'assinatura' in extracted_data:
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