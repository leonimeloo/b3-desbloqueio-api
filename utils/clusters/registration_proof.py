from clusters.base_document import BaseDocument

class RegistrationProofCluster:
    '''Validações e extrações de campos relacionadas ao comprovante de registro.
    
    Os documentos são: Comprovante de Endereço e Comprovante de Situação Cadastral.
    '''
    @staticmethod
    def extract_fields(text: str) -> dict:
        '''Extrai os campos relacionados ao comprovante de registro.'''
        
        extrair_dados_pessoais = BaseDocument.document_question_answering(text, {
            "nome": "Qual é o nome completo ou nomes de pessoas citados no texto?",
            "razao_social": "Qual é a razão social citados no texto?",
            "endereco": "Qual é o endereço informado?",
        })
        
        nome = extrair_dados_pessoais.get("nome", "")
        razao_social = extrair_dados_pessoais.get("razao_social", "")
        endereco = extrair_dados_pessoais.get("endereco", "")
        cpf = BaseDocument.get_cpf(text)
        email = BaseDocument.get_email(text)
        telefone = BaseDocument.get_phone_number(text)
        
        return {
            "nome": nome,
            "razao_social": razao_social,
            "endereco": endereco,
            "cpf": cpf,
            "email": email,
            "telefone": telefone,
        }

    def run_checks(extracted_data: dict, expected_data: dict) -> dict:
        '''Executa as validações relacionadas ao comprovante de registro.'''
        
        validations = {}
        failed_fields = []
        approved = True #começa com aprovado, se houve alguma falha muda pra false
        
        return {}