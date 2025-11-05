import requests
import os
from urllib.parse import urlparse

def get_file(file_uri: str) -> bytes:
    '''
    Conecta ao ServiceNow para baixar o arquivo a ser processado
    '''
    parsed = urlparse(file_uri)
    
    if parsed.scheme in ('http', 'https'):
        response = requests.get(
            file_uri, 
            auth=(str(os.environ.get('USER')), str(os.environ.get('PSWD')))
        )
        return response.content
    else:
        with open(file_uri, 'rb') as file:
            return file.read()