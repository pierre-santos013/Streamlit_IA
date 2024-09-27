import json
import streamlit as st
import datetime
import os
import assemblyai as aai
import requests
from utils import config




def make_api_request(keyword, transcription):
    payload = {
        "keyword": keyword,
        "text": transcription,
    }
    #response = requests.post("http://10.1.254.180:8000/process", json=payload)
    response = requests.post("http://127.0.0.1:8000/process", json=payload)
    return response.json()

def make_api_trascription(file_path):
    try:
        with open(file_path, 'rb') as f:
            files = {'audio': (os.path.basename(file_path), f, 'audio/gsm')}  # Certifique-se de que o tipo MIME está correto.
            response = requests.post("http://10.1.254.180:8000/transcribeaudio", files=files)
        return response.json()
    except aai.TranscriptError as e:
        st.error(f"Arquivo não possui audio: ")
        return None

def limpar_chat():
    st.rerun()
    st.session_state.input_text = ""
    st.session_state.chat = ""
    st.session_state.comun = ""
    st.session_state.ticket = ""
    st.session_state.calls = ""
    st.session_state.botao = False
    st.session_state.transcricao = []
    # Redesenhar a interface sem os dados antigos
    
def dividir_texto(texto):
    partes = {
        "Ticket": "",
        "Interação Chat": "",
        "Comunicação": "",
        "Ligações": ""
    }
    
    idx_ticket = texto.find('ticket:')
    idx_chat = texto.find('Interação Chat:')
    idx_comunicacao = texto.find('Comunicação:')
    idx_ligacoes = texto.find('Ligações:')

    if idx_ticket != -1:
        partes["Ticket"] = texto[idx_ticket:texto.find('Interação Chat:')].strip()
    if idx_chat != -1:
        partes["Interação Chat"] = texto[idx_chat:texto.find('Comunicação:')].strip()
    if idx_comunicacao != -1:
        partes["Comunicação"] = texto[idx_comunicacao:texto.find('Ligações:')].strip()
    if idx_ligacoes != -1:
        partes["Ligações"] = texto[idx_ligacoes:].strip()

    return partes

def criar_json(partes):
    json_data = {
        "Ticket": partes["Ticket"].replace('Ticket:', '').strip(),
        "Interação Chat": partes["Interação Chat"].replace('Interação Chat:', '').strip(),
        "Comunicação": partes["Comunicação"].replace('Comunicação:', '').strip(),
        "Ligações": partes["Ligações"].replace('Ligações:', '').strip()
    }
    
    return json.dumps(json_data, indent=4)

def get_calls(calls:str)->list:
    """
    Extrai os links de ligações de uma string de entrada.

    Args:
    calls: Uma string contendo informações de ligações, onde cada
    ligação está separada por duas quebras de linha ("\n\n") e o link
    é identificado após a sequência ": ".

    Returns:
    Uma lista com os links das ligações extraídos da string de entrada.
    """
                    
    links=[]
    for chamada in calls.split("\n\n"):
        link = chamada.split(': ')[1]
        links.append(link)
# retorna uma lista com os links de ligações
    return links   

def get_chamada(info:str)->list:
    ''' Extrai os links de ligações de uma string de entrada.
        Args:
        info: Uma string contendo informações de ligações, onde cada
        ligação está separada por duas quebras de linha ("\n\n") 
        Returns:
        Uma lista com os informações da ligação data, nome do agente e link.
    ''' 

    parte = info.split("\n\n")
    texto =[]
    for i in parte:
        text =i.strip()
        texto.append(text)
    #return texto
    #chamada = get_chamada(info) # chamada da função
    resultado = []
    for dados in texto:
        if "agente" not in dados:
            data = dados.split("]")[0][1:]
            chamada = dados.split("Chamada ")[1].split(" ")[0]
            name = "não encontrado"  
            link = dados.split(": ")[1]
            retorno = [data, chamada, name, link]
            resultado.append(retorno) 
        else:
            # Caso a palavra "agente" seja encontrada
            name = dados.split("agente ")[1].split(": ")[0]  # Pegando apenas o nome do agente
            link = dados.split("agente ")[1].split(": ")[1]
            data = dados.split("]")[0][1:]  # Pegando a data entre colchetes
            chamada = dados.split("Chamada ")[1].split(" ")[0]
            retorno = [data, chamada, name, link] 
            resultado.append(retorno) 
    return resultado

def download_file(url, save_path):
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            return True
        else:
            return False
    except Exception as e:
        st.error(f"Erro ao baixar o arquivo: {e}")
        return False

def transcribe_audio(filepath):
    transcriber = aai.Transcriber()
    try:
        transcript = transcriber.transcribe(filepath, config=config)
        if transcript.status == aai.TranscriptStatus.error:
            response = f'Arquivo sem audio {transcript.error}'
        else:
            response = ""
            for utterance in transcript.utterances:
                
                time_str = convert_milliseconds(utterance.start)

                response += f"[{time_str}]- Speaker {utterance.speaker}: {utterance.text}\n\n"
                return response
            
    except aai.TranscriptError as e:
        st.error(f"Arquivo não possui audio: ")
        return None
        
def convert_milliseconds(ms):
    return str(datetime.timedelta(milliseconds=ms)).split('.')[0]

def ligacao():
            lig_parse=[]
            for lig_group in st.session_state.dados_call: 
                lig_parse.append(lig_group)
            return lig_parse 
