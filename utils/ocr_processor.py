import io
from pypdf import PdfReader
from pdf2image import convert_from_bytes
import numpy as np
import pytesseract
from typing import List, Tuple, Dict, Optional
import logging
from gliner import GLiNER
from paddleocr import PaddleOCR

import cv2
import json
import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

def read_pdf(read_file: bytes) -> Optional[str]:
    '''
    Extrai o texto selecionável de um arquivo PDF.
    '''
    with io.BytesIO(read_file) as pdf_file:
        try:
            text = str()
            pdf = PdfReader(pdf_file)
            n_pages = len(pdf.pages)
            count = 0
            while count < n_pages:
                page_object = pdf.pages[count]
                text += page_object.extract_text()
                count += 1 
            return text
            
        except Exception as e: 
            logging.error(f'Erro: {e}')
            return None
        
def read_ocr(read_file: bytes) -> Optional[str]:
    '''
    Extrai o texto de um arquivo PDF utilizando OCR.
    '''
    images = convert_from_bytes(read_file)

    final_text = []
    for img in images:
        text = pytesseract.image_to_string(img, lang='por')
        final_text.append(text)

    return '\n'.join(final_text)

def paddle_read_ocr(read_file: bytes) -> Optional[str]:
    images = convert_from_bytes(read_file)

    ocr = PaddleOCR(use_doc_orientation_classify=False,use_doc_unwarping=False,use_textline_orientation=False)

    final_text = str()
    for img in images:
        img_np = np.array(img)
        result = ocr.predict(img_np)
        if isinstance(result, dict) and "res" in result and "rec_texts" in result["res"]:
            texts = result["res"]["rec_texts"]
            page_text = "\n".join(texts)
            final_text += page_text + "\n\n"

    return final_text

def _reconstruir_bloco_de_texto(deteccoes_coluna):
        """
        (VERSÃO CORRIGIDA FINAL) Agrupa detecções em linhas PRIMEIRO,
        e DEPOIS ordena as palavras dentro de cada linha para garantir a ordem de leitura correta.
        """
        if not deteccoes_coluna:
            return ""

        # 1. Pré-ordena todas as detecções da coluna por Y para facilitar o agrupamento
        deteccoes_sorted_y = sorted(deteccoes_coluna, key=lambda item: item['y'])

        # 2. Agrupa as detecções em linhas
        linhas_agrupadas = []
        if deteccoes_sorted_y:
            linha_atual = [deteccoes_sorted_y[0]]
            ultima_pos_y = deteccoes_sorted_y[0]['y']
            ultima_altura = deteccoes_sorted_y[0]['height']

            for i in range(1, len(deteccoes_sorted_y)):
                det_atual = deteccoes_sorted_y[i]
                tolerancia_y = ultima_altura / 2
                
                if abs(det_atual['y'] - ultima_pos_y) <= tolerancia_y:
                    # Se está na mesma linha, adiciona à lista da linha atual
                    linha_atual.append(det_atual)
                else:
                    # Se é uma nova linha, guarda a linha anterior e começa uma nova
                    linhas_agrupadas.append(linha_atual)
                    linha_atual = [det_atual]
                
                ultima_pos_y = det_atual['y']
                ultima_altura = det_atual['height']
            
            # Guarda a última linha processada
            linhas_agrupadas.append(linha_atual)

def ordenar_e_agrupar_texto(ocr_result):
    """
    Leva em conta o sistema de coordenadas
    invertido da imagem para montar o texto na ordem correta.
    """
    if not ocr_result or not ocr_result[0]:
        return ""

    resultado_ocr = ocr_result[0]

    if 'dt_polys' not in resultado_ocr or 'rec_texts' not in resultado_ocr:
        return ""

    detections = []
    coordenadas_x = []
    for box, text in zip(resultado_ocr['dt_polys'], resultado_ocr['rec_texts']):
        if not isinstance(box, (list, np.ndarray)) or len(box) < 4:
            continue
        detections.append({
            "text": text, "x": box[0][0], "y": box[0][1],
            "height": abs(box[2][1] - box[0][1])
        })
        coordenadas_x.append(box[0][0])

    if not detections:
        return ""

    ponto_medio_x = np.median(coordenadas_x)
    
    coluna_esquerda = [d for d in detections if d['x'] < ponto_medio_x]
    coluna_direita = [d for d in detections if d['x'] >= ponto_medio_x]

    texto_da_direita_visual = _reconstruir_bloco_de_texto(coluna_esquerda)
    texto_da_esquerda_visual = _reconstruir_bloco_de_texto(coluna_direita)
    
    final_text = str(texto_da_esquerda_visual or "") + "\n\n" + str(texto_da_direita_visual or "")

    print("\n--- TEXTO RECONSTRUÍDO E ORDENADO ---")
    print(final_text)
    print("-------------------------------------------------")
    
    return final_text

# def extract_rotuled_data(text: str, labels: List[str]) -> List[str]:
#     model = GLiNER.from_pretrained("urchade/gliner_base")
#     entities = model.predict_entities(text, labels)
#     people_set = set()

#     people = []

#     for item in entities:
#         text = item["text"]
#         label = item["label"]
#         text_lower = text.lower()

#         if label == "Person" and text_lower not in people_set:
#             people_set.add(text_lower)
#             people.append(text)

#     return people

def extract_rotuled_data(text: str, labels: List[str]) -> List[str]:
    structure = {
        "name": "verificar_pessoas",
        "description": "Identifique e retorne todas as pessoas (Nome completo) mencionadas no texto.",
        "parameters": {
            "type": "object",
            "properties": {
                "nome": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "Nome completo da pessoa"
                },
            },
            "required": ["nome"],
            "additionalProperties": False
        }
    }
    
    system_prompt = (
        "Extraia todas as pessoas mencionados no texto, inclusive o NOME DO FINANCIADO."
        "Retorne um dicionário JSON com uma lista contendo: 'Nome completo da pessoa'."
    )

    user_prompt = f"Extraia os dados mencionados.\n\nTexto:\n{text}"

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        functions=[structure],
        function_call={"name": "verificar_pessoas"},
        temperature=0.0
    )
    
    arguments = response['choices'][0]['message']['function_call']['arguments']

    try:
        structured_data = json.loads(arguments)["nome"]
        logging.info(f"[EXTRACT] Pessoas extraídas: {arguments} - data: {structured_data}")
    except Exception:
        structured_data = []

    return structured_data