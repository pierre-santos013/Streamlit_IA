import streamlit as st
import pymysql
import requests
import os
import matplotlib.pyplot as plt
import json
import ast

st.title("LISTA BANCO DE DADOS")
st.divider()
st.header('Arquivos disponíveis:')
st.write('\n\n')

def plot_sentiments(data, title):
    labels = list(data.keys())
    values = list(data.values())
        
    plt.figure(figsize=(8, 4))
    plt.bar(labels, values, color='skyblue')
    plt.xlabel('Sentimentos')
    plt.ylabel('Intensidade')
    plt.title(title)
    st.pyplot(plt)


# Conecte-se ao banco de dados MySQL
connection = pymysql.connect(
    host='localhost',
    user='root',
    password='root123',
    database='AudioDatabase'
)

cursor = connection.cursor()

# Obtenha a lista de arquivos de áudio do banco de dados
sql = "SELECT id, filename FROM AudioFiles"
cursor.execute(sql)
audio_data = cursor.fetchall()



# Verifique se existe transcrição correspondente ao audio_id na tabela Transcriptions
for audio_id, audio_file in audio_data:
    with st.container(border=True):

        st.write(f"ID: {audio_id} - {audio_file}")

        # Verificar se há transcrição para o audio_id
        sql_transcription = "SELECT transcription FROM Transcriptions WHERE audio_id = %s"
        cursor.execute(sql_transcription, (audio_id,))
        transcription_data = cursor.fetchone()

        if transcription_data:
            # Exibir a transcrição dentro de um st.expander
            with st.expander(f"Ver Transcrição de {audio_file}"):
                st.write(transcription_data[0])
        else:
            # Mostrar botão para realizar a transcrição
            if st.button(f"Transcrever ", key=f"transcribe_{audio_id}"):
                response = requests.get(f"http://localhost:5000/transcrever/{audio_id}")
                if response.status_code == 200:
                    st.write(f"Transcrição do arquivo {audio_file}:")
                    st.text(response.text)
                else:
                    st.write(f"Erro ao transcrever o arquivo {audio_file}: {response.status_code}")

# analise de sentimento 

        sql_sent_atendente = "SELECT classe, sentimentos, motivo FROM AnaliseAtendente WHERE audio_id = %s"
        cursor.execute(sql_sent_atendente, (audio_id,))
        atendente_data = cursor.fetchone()

        sql_sent_cliente = "SELECT classe, sentimentos, motivo FROM AnaliseCliente WHERE audio_id = %s"
        cursor.execute(sql_sent_cliente, (audio_id,))
        cliente_data = cursor.fetchone()
        

        
        if cliente_data:
            with st.expander(f"Ver Analise de sentimento: {audio_file}"):
                   

                classe_cliente = cliente_data[0]
                sentimentos_cliente = ast.literal_eval(cliente_data[1])  # Converter string para dicionário
                motivos_cliente = ast.literal_eval(cliente_data[2]) 

                classe_atendente = atendente_data[0]
                sentimentos_atendente = ast.literal_eval(atendente_data[1])  # Converter string para dicionário
                motivos_atendente = ast.literal_eval(atendente_data[2]) 
                
                
                    # plotar gráfico cliente    
                st.header("Sentimentos - Cliente")
                plot_sentiments(sentimentos_cliente, f"Classe: {classe_cliente}") 

                st.write(f'Classe: {classe_cliente}')
                #st.write(f'Sentimentos: {sentimentos_cliente}')
                #st.write(f'Motivos: {motivos_cliente}') 

                # motivos

                st.subheader("Principais Motivos - Cliente")
                for i, motivo_c in enumerate(motivos_cliente, start=1):
                    st.markdown(f'**Motivo {i}**: {motivo_c}')

                 
                st.divider()

                # plotar gráfico Atendente.  
                st.header("Sentimentos - Atendente")
                plot_sentiments(sentimentos_atendente, f"Classe: {classe_atendente}")

                st.write(f'Classe: {classe_atendente}')
                #st.write(f'Sentimentos: {sentimentos_atendente}')
                #st.write(f'Motivos: {motivos_atendente}')    

                # Exibir principais motivos.
                st.subheader("Principais Motivos - Atendente")
                for i, motivo_a in enumerate(motivos_atendente, start=1):
                    st.markdown(f'**Motivo {i}**: {motivo_a}')







            payload = {
                    "keyword": "sentimento",
                    "text": transcription_data[0],
                    }
        else:
            if st.button(f"analisar ", key=f"analise_{audio_id}"): 
                

                response = requests.post("http://127.0.0.1:5000/process2", json=payload)
                if response.status_code == 200:
                    st.write(f"Transcrição do arquivo {audio_file}:")
                    st.text(response.text)
                else:
                    st.write(f"Erro ao transcrever o arquivo {audio_file}: {response.status_code}")

# Feche a conexão
cursor.close()
connection.close()
