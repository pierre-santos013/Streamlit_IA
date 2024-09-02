
# 02/09/2024
# incluido gráfico de analise de sentimento
# 


import os
import streamlit as st
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
import json

# Configuração das chaves de API
api_key_groq = st.secrets["api_keys"]["api_key3"]
api_key_gemini = st.secrets["api_keys"]["api_key1"]
aai.settings.api_key = st.secrets["api_keys"]["api_key5"]  
client = Groq(api_key=api_key_groq)

# Configuração da API Gemini
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

#config = aai.TranscriptionConfig(speech_model=aai.SpeechModel.best, language_code="pt")
config = aai.TranscriptionConfig(speech_model=aai.SpeechModel.best, speaker_labels=True, language_code="pt")

def limpar_chat():
    st.session_state.chat = []
    st.session_state.history = []
    st.session_state.transcricao_feita = False
    
    if os.path.exists("audio_temp.flac"):
        os.remove("audio_temp.flac")
        os.remove("transcription.docx")
        os.remove("transcription.pdf")


def transcribe_audio(filepath):
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(filepath, config=config)
    if transcript.status == aai.TranscriptStatus.error:
        response = transcript.error
    else:
        #response = transcript.text
        response = ""
        for utterance in transcript.utterances:
            response += f"Speaker {utterance.speaker}: {utterance.text}\n"

    return response

def export_to_pdf(transcription):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in transcription:
        line_str = line.encode('latin1', 'ignore').decode('latin1') #- teste alteração    
        pdf.multi_cell(0, 10, line_str) #- teste alteração
        
    pdf_file = "transcription.pdf"
    pdf.output(pdf_file)
    return pdf_file

def export_to_docx(transcription):
    doc = Document()
    for line in transcription:
        doc.add_paragraph(line)
    doc_file = "transcription.docx"
    doc.save(doc_file)
    return doc_file

def role_to_streamlit(role):
    return "assistente" if role == "model" else role

def make_api_request(keyword, transcription):
    payload = {
        "keyword": keyword,
        "text": transcription,
    }
    response = requests.post("http://127.0.0.1:5000/process", json=payload)
    return response.json()

def plot_sentiments(data, title, key):
        labels = list(data.keys())
        values = list(data.values())
        
        plt.figure(figsize=(8, 4))
        plt.bar(labels, values, color='skyblue')
        plt.xlabel('Sentimentos')
        plt.ylabel('Intensidade')
        plt.title(title)
        #st.pyplot(plt)
        # Salvar o gráfico como imagem
        img_path = os.path.join(f"{key}_sentiment_graph.png")
        plt.savefig(img_path)

        # Armazenar a imagem no st.session_state
        st.session_state[key] = img_path

        # Exibir o gráfico na interface
        st.pyplot(plt)
        plt.close()



def main():
    st.title("💬 Chat - Transcription audio 🎙🔉")

    for message in st.session_state.chat:
        role = "user" if message["role"] == "user" else "assistant"
        with st.chat_message(role):
            st.markdown(message['text'])

    if "cliente_graph" not in st.session_state:
        st.session_state['cliente_graph'] = None
    if "atendente_graph" not in st.session_state:
        st.session_state['atendente_graph'] = None

    if st.session_state['cliente_graph']:
        st.image(st.session_state['cliente_graph'], caption="Gráfico de Sentimentos - Cliente")
    if st.session_state['atendente_graph']:
        st.image(st.session_state['atendente_graph'], caption="Gráfico de Sentimentos - Atendente")
 

    if "chat" not in st.session_state:
        st.session_state.chat = []
        st.session_state.history = []
        st.session_state.transcricao = []

    if "transcricao_feita" not in st.session_state:
        st.session_state.transcricao_feita = False
       
    if "transcricao" not in st.session_state:
        st.session_state.transcricao = ""

    if "pdf_downloads" not in st.session_state:
        st.session_state.pdf_downloads = 0
    if "docx_downloads" not in st.session_state:
        st.session_state.docx_downloads = 0


#sidebar ----------------------------------------------------------------------
    with st.sidebar:
        st.button("NOVO CHAT", on_click=limpar_chat)
        st.sidebar.divider()
        arquivo_carregado = st.sidebar.file_uploader("Carregar arquivo de áudio (GSM ou MP3)")
       

        #botoes de download sidebar
    if st.session_state.transcricao_feita:
            
        with open("transcription.pdf", "rb") as f:
            st.sidebar.download_button(
                label=f"Download PDF ({st.session_state.pdf_downloads})",
                data=f,
                file_name="transcription.pdf",
                mime="application/pdf"
            )

        with open("transcription.docx", "rb") as f:
            st.sidebar.download_button(
                label=f"Download DOCX ({st.session_state.docx_downloads})",
                data=f,
                file_name="transcription.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

            # Entrada para o keyword e botão para enviar a transcrição
        keyword = st.sidebar.text_input("Keyword para API", "aprovar")
        if st.sidebar.button("Enviar para Análise"):             

            if keyword =="sentimento":
                response = make_api_request(keyword, st.session_state.transcricao)
                dados = response['result'].split("```")[1]
                dados_final = json.loads(dados)

                # plotar gráfico cliente    
                st.header("Sentimentos - Cliente")
                plot_sentiments(dados_final["cliente"]["sentimentos"], f"Classe: {dados_final['cliente']['classe']}", key="cliente_graph")

                # Exibir principais motivos.
                st.subheader("Principais Motivos - Cliente")
                motivo_cli = dados_final["cliente"]["razao_possivel"]

                for i, motivo_c in enumerate(motivo_cli, start=1):
                    st.markdown(f'**Motivo {i}**: {motivo_c}')

                # plotar gráfico Atendente.  
                st.header("Sentimentos - Atendente")
                plot_sentiments(dados_final["atendente"]["sentimentos"], f"Classe: {dados_final['atendente']['classe']}", key="atendente_graph")


                # Exibir principais motivos.
                st.subheader("Principais Motivos - Atendente")
                motivo_aten= dados_final["atendente"]["razao_possivel"]   

                for i, motivo_a in enumerate(motivo_aten, start=1):
                    st.write(f'**Motivo {i}**: {motivo_a}')                                                                   
                                
            else:    
                response = make_api_request(keyword, st.session_state.transcricao)
                resp_api = response.get('result','')
                st.markdown(f"### Resposta da API: \n```{resp_api}```")
                #st.code(response, language='json')
                st.session_state.chat.append({"role": "assistant", "text": f"**Resposta da API**:\n\n {resp_api}"})



#inicio do chatbot --------------------------------------------------------------------

    
    if prompt := st.chat_input("Como posso ajudar?"):
        st.session_state.chat.append({"role": "user", "text": prompt})
        st.session_state.history.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        try:

            response = client.chat.completions.create(
                messages=st.session_state.history,
                model="llama3-70b-8192"
            )
            response_text = response.choices[0].message.content
            with st.chat_message("assistant"):
                st.write("IA-Groq:")
                st.markdown(response_text)
            st.session_state.chat.append({"role": "assistant", "text": response_text})
            st.session_state.history.append({"role": "assistant", "content": response_text})    

            
        except Exception as e:  # Use uma exceção mais específica se possível
        # Caso ocorra um erro com o Groq, usar o Gemini como fallback
            try:
                response = model_g.generate_content(prompt)
                response_text = response.text  # Ajuste conforme a estrutura real da resposta
            except Exception as gemini_error:
                # Caso o Gemini também falhe
                response_text = "Desculpe, ocorreu um erro ao processar sua solicitação."

            with st.chat_message("assistant"):
                st.write("IA-Gemini:")
                st.markdown(response_text)
                # Atualizando o estado com a resposta do Gemini
                st.session_state.chat.append({"role": "assistant", "text": response_text})
                st.session_state.history.append({"role": "assistant", "content": response_text})
        
            

# ------------------- AUDIO -----------------------------------------
    

    if arquivo_carregado:
        st.sidebar.markdown("# PLAY AUDIO 🔉 ")

        @st.cache_data
        def carregar_audio(arquivo_carregado):
            return arquivo_carregado.read()

        audio_data = carregar_audio(arquivo_carregado)

        #validação extenção do arquivo
        if arquivo_carregado.name.endswith(".gsm"):
            temp_filename = "audio_temp.flac"
            with open(temp_filename, "wb") as f:
                f.write(audio_data)
            AudioSegment.from_file(temp_filename, format="gsm").export(temp_filename, format="flac")
            audio_data = open(temp_filename, "rb").read()
        else:
            temp_filename = "audio_temp.flac"
            with open(temp_filename, "wb") as f:
                f.write(audio_data)

        st.sidebar.audio(temp_filename, format="audio/mpeg", loop=False)

        if not st.session_state.transcricao_feita and st.sidebar.button("Fazer transcrição"):

            st.write("Realizando o tratamento do áudio...")

            st.session_state.file_path = temp_filename
            transcription = transcribe_audio(st.session_state.file_path)
            #st.session_state.transcricao_feita = True

            st.session_state.chat.append({"role": "system", "text": f"Transcrição: \n {transcription}"})
            st.session_state.history.append({"role": "system", "content": f"Transcrição: \n {transcription}"})
            #st.session_state.transcricao.append(f'{transcription}')

            with st.expander("Mostrar lista"):
                st.write(f"Transcrição: \n {transcription}")

            st.write("Processando transcrição ...")

            #prompt4 = f''' {transcription} retorne uma breve analise da transcrição. '''
            prompt5 = f''' {transcription} mostre a transcrição como se fosse uma timeline informando o speaker e o texto não apresente o tempo. '''

            
            try:
                resp = model_g.generate_content(prompt5)
                response_final = resp.text

                with st.chat_message("assistente"):
                    st.write("Resposta Gemini")
                    st.markdown(response_final)
                    st.session_state.chat.append({"role": "assistente", "text": response_final})
                    st.session_state.history.append({"role": "assistant", "content": response_final})

            except ValueError as e:
                st.error("Erro ao processar a resposta do modelo Gemini. Usando o modelo Groq para a transcrição.")
                response_final = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt5}],
                    model="llama3-70b-8192"
                ).choices[0].message.content

        # apresentação na tela 
                with st.chat_message("assistente"):
                    st.write("Resposta Groq")
                    st.markdown(response_final)
                    st.session_state.chat.append({"role": "assistente", "text": response_final})
                    st.session_state.history.append({"role": "assistant", "content": response_final})
             

            pdf_file = export_to_pdf(response_final.splitlines())
            docx_file = export_to_docx(response_final.splitlines())

            st.session_state.transcricao = response_final
            st.session_state.transcricao_feita = True
            st.session_state.pdf_downloads += 1
            st.session_state.docx_downloads += 1

                # Mostrar os botões de download após a transcrição
                
            with open("transcription.pdf", "rb") as f:
                st.sidebar.download_button(
                    label=f"Download PDF ({st.session_state.pdf_downloads})",
                    data=f,
                    file_name="transcription.pdf",
                    mime="application/pdf"
                )

            with open("transcription.docx", "rb") as f:
                st.sidebar.download_button(
                    label=f"Download DOCX ({st.session_state.docx_downloads})",
                    data=f,
                    file_name="transcription.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
            keyword = st.text_input("Keyword para API", "aprovar")
            if st.button("Enviar para Análise"):
                response = make_api_request(keyword, st.session_state.transcricao)
                resp_api = response.get('result','')
                st.markdown(f"### Resposta da API: \n```{resp_api}```")
                #st.code(response, language='json')
                st.session_state.chat.append({"role": "assistant", "text": f"**Resposta da API**:\n\n {resp_api}"})
            
                
                    
                    

            
    
    #st.sidebar.write("realize a interação")        

if __name__ == "__main__":
    main()
