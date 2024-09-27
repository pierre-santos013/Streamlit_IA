import json
import streamlit as st
import datetime
import os
from pydub import AudioSegment
from groq import Groq
import google.generativeai as genai
from docx import Document
from fpdf import FPDF
import assemblyai as aai
from pydub.utils import which
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import matplotlib.pyplot as plt
import requests
import re
import pymysql

api_key_groq = st.secrets["api_keys"]["api_key3"]
api_key_gemini = st.secrets["api_keys"]["api_key1"]
aai.settings.api_key = st.secrets["api_keys"]["api_key5"]  
client = Groq(api_key=api_key_groq)

genai.configure(api_key=api_key_gemini)
generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}
safety_settings = {
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE
}
model_g = genai.GenerativeModel(model_name='models/gemini-1.5-flash-latest', generation_config=generation_config, safety_settings=safety_settings)
# configuração assemblyia
config = aai.TranscriptionConfig(speech_model=aai.SpeechModel.best, speaker_labels=True, language_code="pt")


connection = pymysql.connect(
    host='localhost',
    user='root',
    password='root123',
    database='basedados'
)

cursor = connection.cursor()





# Funções 
def make_api_request(keyword, transcription):
    payload = {
        "keyword": keyword,
        "text": transcription,
    }
    response = requests.post("http://127.0.0.1:8000/process", json=payload)
    return response.json()

def make_api_trascription(file_path):
    try:
        with open(file_path, 'rb') as f:
            files = {'audio': (os.path.basename(file_path), f, 'audio/gsm')}  # Certifique-se de que o tipo MIME está correto.
            response = requests.post("http://127.0.0.1:8000/transcribeaudio", files=files)
        return response.json()
    except aai.TranscriptError as e:
        st.error(f"Arquivo não possui audio: ")
        return None

def limpar_chat():
    st.session_state.input_text = ""
    st.session_state.chat = ""
    st.session_state.comun = ""
    st.session_state.ticket = ""
    st.session_state.calls = ""
    st.session_state.botao = False
    # Redesenhar a interface sem os dados antigos
    st.rerun()

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




# Funções mysql

def verificar_ticket_existe(ticket_id):
    with connection.cursor() as cursor:
        sql = "SELECT COUNT(*) FROM tickets WHERE id = %s"
        cursor.execute(sql, (ticket_id,))
        result = cursor.fetchone()
        return result[0] > 0  # Retorna True se o ticket já existir

def verificar_link_existe(link):
    with connection.cursor() as cursor:
        sql = "SELECT COUNT(*) FROM ligacoes WHERE id = %s"
        cursor.execute(sql, (link,))
        result = cursor.fetchone()
        return result[0] > 0  # Retorna True se o ticket já existir
    
def inserir_dados_ligacao():
    # Inserir dados das ligações
    ticket_id = st.session_state.ticket.split('ticket/')[1]
    ligparse1 = ligacao()  # A função ligacao retorna a lista de dados
    inserido_sucesso = False  # Variável de controle para saber se ao menos uma ligação foi inserida

    try:
        with connection.cursor() as cursor:
            i=0
            for lig in ligparse1:
                link = lig[3]
                data_ligacao_str = lig[0]
                origem_call = lig[1]
                name_atendente = lig[2]
                data_ligacao = datetime.datetime.strptime(data_ligacao_str, '%d/%m/%Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
                transcription = st.session_state.transcricao[i][0]['transcription']
                file_path = st.session_state.transcricao[i][0]['file_path'] 
                file_name = st.session_state.transcricao[i][0]['filename'] 

                # Verificar se o link já existe no banco de dados
                sql_verificar = "SELECT COUNT(1) FROM ligacoes WHERE link = %s"
                cursor.execute(sql_verificar, (link,))
                resultado = cursor.fetchone()

                
                    
                i+=1

                if resultado[0] == 0:  # Se o link não existe, inserir
                    # Executar a inserção no banco de dados
                    sql = """
                    INSERT INTO ligacoes (ticket_id, link, data_ligacao, origem_call, name_atendente, transcricao, filename, file_path)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql, (ticket_id, link, data_ligacao, origem_call, name_atendente, transcription, file_name, file_path))
                    inserido_sucesso = True  # Marcar que inserção foi feita
                else:
                    st.info(f"Ligação com o link {link} já existe no banco de dados.")
            
            if inserido_sucesso:
                connection.commit()  # Fazer o commit apenas se algo foi inserido
                st.toast("Todas as novas ligações foram inseridas com sucesso!")
            else:
                st.toast("Nenhuma nova ligação foi inserida.")

    except Exception as e:
        st.error(f"Erro ao inserir ligação: {e}")
        connection.rollback()

def inserir_dados_ticket():   
    ticket_id = st.session_state.ticket.split('ticket/')[1]
    comunicacao = st.session_state.comun
    chat = st.session_state.chat
    try:
        if verificar_ticket_existe(ticket_id):
            no_exist=st.toast("O ticket já existe no banco de dados.")
            return no_exist
        else:
            
            with connection.cursor() as cursor:
                sql = """
                INSERT INTO tickets (id, comunicacao, chat)
                VALUES (%s, %s, %s)
                """
                cursor.execute(sql, (ticket_id, comunicacao, chat))
                connection.commit()

                is_exist = st.toast("Dado inserido com sucesso!")
                
                return is_exist
            inserir_dados_ligacao(ticket_id)
    except Exception as e:
        st.error(f"Erro ao inserir dado: {e}")
        connection.rollback()







def main():
# Inicializar as variáveis na session_state apenas se não existirem
    if "input_text" not in st.session_state:
        st.session_state.input_text = ""
        st.session_state.chat = ""
        st.session_state.comun = ""
        st.session_state.ticket = ""
        st.session_state.calls = ""
        st.session_state.show_results = False
        st.session_state.transcricao = []
        st.session_state.dados_call =""

    st.title("Analise do Atendimento.")
    
#Somente exibe o campo de input e o botão de conversão se não houver texto convertido
    input_text = st.text_area("Cole o texto do ticket aqui", value=st.session_state.input_text)

    if st.button("Converter"):
        if input_text:
            parsed_data = dividir_texto(input_text)
            json_result = criar_json(parsed_data)
            json_result = json.loads(json_result)

                # Atualizar session_state com os valores convertidos
            st.session_state.input_text = input_text
            st.session_state.chat = json_result['Interação Chat']
            st.session_state.comun = json_result['Comunicação']
            st.session_state.ticket = str(json_result['Ticket']).split("t:")[1] if "t:" in json_result['Ticket'] else json_result['Ticket']
            st.session_state.calls = json_result['Ligações']
                
        else:
            st.warning("Por favor, cole o texto antes de converter.")
    
    if st.button("salvar dados no banco"):
        inserir_dados_ticket()
        inserir_dados_ligacao()
       

# Só exibir os valores armazenados após a conversão
    if st.session_state.input_text:
        st.session_state.show_results = True
        if st.sidebar.button("Nova Análise"):
            limpar_chat()
        st.sidebar.divider()    

    # Exibir os resultados
        st.header("Análise de Interação")

        with st.expander("Interação Chat:"):
            if st.session_state.chat == "":
               st.write(f'TICKET NÃO POSSUI CHAT')
            else:
                st.write(f'{st.session_state.chat}')

        with st.expander("Comunicação:"):    
            st.write(f'{st.session_state.comun}')

        with st.expander("Ticket"):
            st.write(f'{st.session_state.ticket}')
            
                                
        with st.expander("Ligações"):
            if st.session_state.calls == "":
               st.write(f'TICKET NÃO POSSUI CHAMADAS') 
            else:
        # link da ligação.
                link_call = get_calls(st.session_state.calls)
                st.write(f'Total de chamadas: {len(link_call)}')
                dados_call = get_chamada(st.session_state.calls)
                st.session_state.dados_call = dados_call
                st.write(dados_call)
                dados_geral= st.empty()
                st.write(link_call)
                
        
        if st.session_state.transcricao:
            
            with st.expander("Transcrição"):          
                t= []
                for item in st.session_state.transcricao:       
                    for  it in item:       
                        h=it['transcription']
                        st.write(it['transcription'])
                        t.append(h)
                st.write(t)

                with dados_geral.container():   
                    
                    st.write(st.session_state.dados_call)
                    st.write(st.session_state.transcricao)
                    

    # Exibir o botões de analise        
        if st.session_state.chat == "":
            pass
        else:
            if st.sidebar.button("Resumo Chat"): 
                keyword= "resumo"    
                response = make_api_request(keyword, st.session_state.chat)
                st.markdown(f"Resumo da interação: \n\n {response["result"]}")

        if st.sidebar.button("Análise de sentimento"): 
            keyword= "sentimento"
            if st.session_state.chat:
                with st.spinner(f"Analisando a Interação..."):
                    response = make_api_request(keyword, st.session_state.chat)
                    st.markdown(f"Sentimentos Interação: \n\n {response["result"]}")  
            if not st.session_state.transcricao:
                st.write("necessário realizar a transcrição antes da análise")
            else:
                sent_transcription= st.session_state.transcricao   
                response = make_api_request(keyword, sent_transcription)
                pass

        if st.sidebar.button("Análise de venda"): 
            keyword= "aprovar"
            response = make_api_request(keyword, st.session_state.chat)
            st.markdown(f"Análise de venda \n\n {response["result"]}")      

        if st.sidebar.button("Análise do comentário"): 
            keyword= "comentario"
            response = make_api_request(keyword, st.session_state.chat)
            st.markdown(f"Análise de venda \n\n {response["result"]}")

        if st.sidebar.button("Análise de cancelamento"): 
            keyword= "cancelamento"
            response = make_api_request(keyword, st.session_state.chat)
            st.markdown(f"Análise de cancelamento \n\n {response["result"]}")
        
        if st.sidebar.button('Transcrever chamadas'):
            save_folder = r'C:\\Users\\Azevedo Cobretti\\OneDrive\\Documentos\\BD_audios\\audio2'
            if not os.path.exists(save_folder):
                os.makedirs(save_folder)

            name_link = st.session_state.ticket.split("t/")[1]
            transcricoes = []
            with st.spinner(f"Baixando {len(link_call)} arquivos..."):
                for idx, lin in enumerate(link_call):
                    
                    file_name = os.path.join(save_folder, f"{name_link}_{idx + 1}.gsm")

                    if download_file(lin, file_name):
                        st.toast(f"Arquivo {idx + 1} baixado com sucesso!")
                        
                        #tentar transcrever o arquivo e armazenar 
                        with st.spinner(f"realizando a transcrição do arquivo {idx + 1} "):
                            
                            response = make_api_trascription(file_name)                          
                            
                            transcricoes.append(response)
                            
                    else:
                        st.error(f"Falha ao baixar o arquivo {idx + 1}.")

            
            st.session_state.transcricao = transcricoes

       





           
            
            


if __name__ == '__main__':
    main()
