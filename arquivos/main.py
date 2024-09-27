# validados: transcribe2, process
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Dict, Optional
from werkzeug.utils import secure_filename
import datetime
import logging
import os
from fpdf import FPDF
import datetime

import speech_recognition as sr
from pydub import AudioSegment

import assemblyai as aai
from groq import Groq
import google.generativeai as genai

import pymysql
import json

from pydantic import BaseModel, Field

# Carrega os prompts
import arquivos.Prompts as Prompts
prompts = Prompts.prompts


# Configurações gerais
app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'gsm', 'mp3', 'flac'}

# Configurações de API
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)
genai.configure(api_key="AIzaSyDWnRq7MoCV3vzH98FmMLuVFFU7aOxnLdQ")

ASSEMBLYAI_API_KEY = "0dd6e4398bb34fca86494411ff025f07"
aai.settings.api_key = ASSEMBLYAI_API_KEY

# Configurações do banco de dados
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root123',
    'database': 'AudioDatabase'
}



# Models para validação de dados
class AudioData(BaseModel):
    audio: UploadFile = File(...)
    keyword: Optional[str] = None
    text: Optional[str] = None

class KeywordData(BaseModel):   
    keyword: Optional[str] = None
    text: Optional[str] = None
    audio_id: Optional[int] = None

class TranscriptionResponse(BaseModel):
    filename: str
    transcription: str
    file_path: str

class AnaliseResponse(BaseModel):
    transcricao: str
    analise: str

class ProcessResponse(BaseModel):
    result: str

class SentimentoRequest(BaseModel):
    keyword: str = "sentimento"
    text: str
    audio_id: int

class Process2Response(BaseModel):
    result: str



# Funções auxiliares
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_to_flac(input_file):
    audio = AudioSegment.from_file(input_file)
    flac_filename = os.path.splitext(input_file)[0] + ".flac"
    audio.export(flac_filename, format="flac")
    return flac_filename

def save_chunk(chunk, index, output_dir='chunks'):
    os.makedirs(output_dir, exist_ok=True)
    chunk_filename = os.path.join(output_dir, f"chunk_{index}.flac")
    chunk.export(chunk_filename, format="flac")
    return chunk_filename

def run_groq(prompt, text):
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": f"{text}: {prompt}"}],
            model="llama3-70b-8192",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        logger.error(f"Error in Groq processing: {e}")
        return None

def run_gemini(prompt, text):
    try:
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        response = model.generate_content(f"{text}: {prompt}")
        return response.text
    except Exception as e:
        logger.error(f"Error in Gemini processing: {e}")
        return "An error occurred while processing the request with the fallback LLM."

def validate_input(keyword, text):
    if not keyword or keyword not in prompts:
        logger.error("Teste Ia_leste: Invalid keyword provided.")
        return False, "Teste Ia_leste: Invalid keyword. Please provide a valid keyword."
    if not text or len(text.strip()) == 0:
        logger.error("Teste Ia_leste: Empty or invalid text provided.")
        return False, "Teste Ia_leste: Text cannot be empty. Please provide valid text."
    return True, ""

def run_with_fallback(prompt, text):
    result = run_groq(prompt, text)

    if not result or len(result.strip()) == 0:
        logger.warning("Erro ao utilizar a Groq, utilizando o Gemini.")
        result = run_gemini(prompt, text)
        
    return result

def convert_milliseconds(ms):
    return str(datetime.timedelta(milliseconds=ms)).split('.')[0]

def log_request_data(id: int, timestamp: str):
    log_filename = 'process_requests.log'
    with open(log_filename, 'a') as log_file:
        log_file.write(f"ID: {id}, Timestamp: {timestamp}\n")




# Rotas da aplicação
@app.post("/transcribe_g", response_model=List[TranscriptionResponse])
async def stt_audio_google(audio: List[UploadFile] = File(...)):
    try:
        transcricoes = []
        for file in audio:
            if file.filename == '':
                raise HTTPException(status_code=400, detail="Nenhum arquivo selecionado")

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                with open(filepath, 'wb') as f:
                    f.write(await file.read())

# Converter o arquivo para .flac se necessário
                if filepath.endswith('.gsm') or filepath.endswith('.mp3'):
                    filepath = convert_to_flac(filepath)

                audio_segment = AudioSegment.from_file(filepath)
                chunk_length_ms = 120000
                chunks = [audio_segment[i:i + chunk_length_ms] for i in range(0, len(audio_segment), chunk_length_ms)]

                recognizer = sr.Recognizer()
                full_transcript = ""

                for i, chunk in enumerate(chunks):
                    chunk_filename = save_chunk(chunk, i)
                    with sr.AudioFile(chunk_filename) as source:
                        audio_data = recognizer.record(source)
                    texto = recognizer.recognize_google(audio_data, language='pt-BR')
                    full_transcript += texto + "\n"
                    os.remove(chunk_filename)

                transcricao_dir = 'transcricoes'
                os.makedirs(transcricao_dir, exist_ok=True)
                transcricao_filename = f"transcricao_{filename}.pdf"
                transcricao_path = os.path.join(transcricao_dir, transcricao_filename)

                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                for line in full_transcript.split("\n"):
                    pdf.multi_cell(0, 10, line)
                pdf.output(transcricao_path)

                transcricoes.append({"filename": filename, "transcription": full_transcript, "file_path": transcricao_path})

            else:
                raise HTTPException(status_code=400, detail=f"Tipo de arquivo inválido para o arquivo {file.filename}")

        return transcricoes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/transcribeaudio", response_model=List[TranscriptionResponse])
async def stt_audio_assembly(audio: List[UploadFile] = File(...)):
    '''
    rota recebe um paylod form/data {audio},
    converte para .flac,
    realiza a trabnscrição e retorna:filename, transcription e file_path.
    '''
    try:
        transcricoes = []
        for file in audio:
            if file.filename == '':
                raise HTTPException(status_code=400, detail="Nenhum arquivo selecionado")

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                with open(filepath, 'wb') as f:
                    f.write(await file.read())

# Converter o arquivo para .flac se necessário
                if filepath.endswith('.gsm') or filepath.endswith('.mp3'):
                    filepath = convert_to_flac(filepath)

                try:
                    #config = aai.TranscriptionConfig(speech_model=aai.SpeechModel.best, language_code="pt")
                    config = aai.TranscriptionConfig(speech_model=aai.SpeechModel.best, speaker_labels=True, language_code="pt")
                    transcriber = aai.Transcriber()
                    with open(filepath, 'rb') as audio_file:
                        transcript = transcriber.transcribe(audio_file, config=config)
                        if transcript.status == aai.TranscriptStatus.error:
                            response = f'Arquivo não contém áudio '
                        else:
                            response = ""
                            for utterance in transcript.utterances:
                                #time_str = convert_milliseconds(utterance["start"])
                                time_str = convert_milliseconds(utterance.start)

                                response += f"[{time_str}]- Speaker {utterance.speaker}: {utterance.text}\n\n"    
                        
                        # Formata a transcrição
                    #transcricao_texto = transcript.text

                except Exception as e:
                    #return jsonify({"error": f"Falha ao transcrever com ambos os serviços: {str(e)}, "}), 500
                    raise HTTPException(detail=f"Arquivo não contem audio : ")

                transcricao_dir = 'transcricoes'
                os.makedirs(transcricao_dir, exist_ok=True)
                transcricao_filename = f"transcricao_{filename}.pdf"
                transcricao_path = os.path.join(transcricao_dir, transcricao_filename)

                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                for line in response.split("\n"):
                    pdf.multi_cell(0, 10, line)
                pdf.output(transcricao_path)

                transcricoes.append({"filename": filename, "transcription": response, "file_path": transcricao_path})

            else:
                raise HTTPException(status_code=400, detail=f"Tipo de arquivo inválido para o arquivo {file.filename}")

        return transcricoes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/analyze", response_model=List[AnaliseResponse])
async def analisar_transcricao(transcricoes: List[str] = Form(...)):
    try:
        analisadas = []
        for transcricao in transcricoes:
            prompt = f"faça um resumo da interação: {transcricao}"

            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": f"{prompt}"}],
                model="llama3-70b-8192",
            )
            analise = chat_completion.choices[0].message.content

            analisadas.append({'transcricao': transcricao, 'analise': analise})

        return analisadas
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/context", response_model=AnaliseResponse)
async def analisar_transcricao2(transcricoes: List[str] = Form(...)):
    try:
        texto_completo = "\n".join(transcricoes)
        prompt = f"faça um resumo da interação: {texto_completo}"

        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": f"{prompt}"}],
            model="llama3-70b-8192",
        )
        analise = chat_completion.choices[0].message.content

        return {"analise": analise}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process", response_model=ProcessResponse)
async def process_request(data: KeywordData):
    keyword = data.keyword
    text = data.text
    audio_id = data.audio_id

    is_valid, error_message = validate_input(keyword, text)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_message)

    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_request_data(data.audio_id, timestamp)

    if keyword in prompts:
        if keyword == "sentimento":
            prompt2 = "Retire dos dados do cliente no dicionário abaixo e retorne em formato json" \
                    "respeitando apenas a seguinte estrutura: " \
                        "{" \
                        "\"cliente\": {" \
                            "\"classe\": " \
                            "\"sentimentos\":  ," \
                            "\"razao_possivel\":  " \
                        "},"\
                        "\"atendente\": {" \
                            "\"classe\":  ," \
                            "\"sentimentos\":  ," \
                            "\"razao_possivel\":  " \
                        "}" \
                        "}" \
                        
            prompt = prompts[keyword]
            response = run_with_fallback(prompt, text)
            result = run_groq(response, prompt2)

        prompt = prompts[keyword]
        result = run_with_fallback(prompt, text)
    else:
        logger.info("Palavra-chave não reconhecida, usando tratamento padrão.")
        #result = run_gemini(f"Processe o seguinte texto: {text}", text)
        result = "Teste Ia_leste: Falha na requisição."

    return {"result": result}


@app.get("/transcrever/{audio_id}")
async def transc_audio_msql(audio_id: int):
    '''
    Faz a transcrição do audio e inclui no banco de dados mysql
    '''
    try:
        # Conecta ao banco de dados
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor(pymysql.cursors.DictCursor)

        # Busca o arquivo de áudio pelo ID
        cursor.execute("SELECT * FROM AudioFiles WHERE id = %s", (audio_id,))
        audio = cursor.fetchone()

        if not audio:
            cursor.close()
            connection.close()
            raise HTTPException(status_code=404, detail="Arquivo de áudio não encontrado")

        # Caminho completo do arquivo de áudio
        audio_path = audio['filepath']

        # Converter o arquivo para .flac se necessário
        if audio_path.endswith('.gsm') or audio_path.endswith('.mp3'):
            audio_path = convert_to_flac(audio_path)

        try:
            config = aai.TranscriptionConfig(speech_model=aai.SpeechModel.best, language_code="pt")
            transcriber = aai.Transcriber()

            # Transcreve o áudio
            with open(audio_path, 'rb') as audio_file:
                transcript = transcriber.transcribe(audio_file, config=config)

            # Formata a transcrição
            transcricao_texto = transcript.text

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Falha ao transcrever com ambos os serviços: {str(e)}, ")

        # Cria e salva o arquivo de transcrição .pdf
        transcricao_dir = 'transcricoes'
        os.makedirs(transcricao_dir, exist_ok=True)
        transcricao_filename = f"transcricao_audio_{audio_id}.pdf"
        transcricao_path = os.path.join(transcricao_dir, transcricao_filename)

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        for line in transcricao_texto.split("\n"):
            pdf.multi_cell(0, 10, line)
        pdf.output(transcricao_path)

        # Insere o caminho do arquivo e a transcrição no banco de dados
        insert_query = """
        INSERT INTO Transcriptions (audio_id, transcription, transcription_path) 
        VALUES (%s, %s, %s)
        """
        cursor.execute(insert_query, (audio_id, transcricao_texto, transcricao_path))
        connection.commit()

        cursor.close()
        connection.close()

        return JSONResponse(content={"message": "Transcrição adicionada ao Banco de dados com sucesso"})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/process2", response_model=Process2Response)
async def process2_request(data: SentimentoRequest):
    keyword = data.keyword
    text = data.text
    audio_id = data.audio_id
    
    is_valid, error_message = validate_input(keyword, text)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_message)
    
    if keyword in prompts:
        if keyword == "sentimento":
            prompt2 = "Retire dos dados do cliente no dicionário abaixo e retorne em formato json " \
                    "respeitando apenas a seguinte estrutura: " \
                        "{" \
                        "\"cliente\": {" \
                            "\"classe\": " \
                            "\"sentimentos\":  ," \
                            "\"razao_possivel\":  " \
                        "},"\
                        "\"atendente\": {" \
                            "\"classe\":  ," \
                            "\"sentimentos\":  ," \
                            "\"razao_possivel\":  " \
                        "}" \
                        "}" 
            prompt = prompts[keyword]
            response = run_with_fallback(prompt, text)
            result = run_groq(response, prompt2)
            dados= result.split("```")[1]
            dados = json.loads(dados)
            print(type(dados))
            classe_cli = str(dados['cliente']['classe'])
            sentimento_cli = str(dados['cliente']['sentimentos'])
            motivo_cli= str(dados['cliente']['razao_possivel'])
            classe_ate = str(dados['atendente']['classe'])
            sentimento_ate = str(dados['atendente']['sentimentos'])
            motivo_ate = str(dados['atendente']['razao_possivel'])
            
            connection = pymysql.connect(**db_config)
            cursor = connection.cursor(pymysql.cursors.DictCursor)

            insert_query = """
            INSERT INTO AnaliseAtendente (audio_id, classe, sentimentos, motivo) 
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(insert_query, (audio_id, classe_ate, sentimento_ate, motivo_ate))
            connection.commit()

            insert_query = """
            INSERT INTO AnaliseCliente (audio_id, classe, sentimentos, motivo) 
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(insert_query, (audio_id, classe_cli, sentimento_cli, motivo_cli))
            connection.commit()

            cursor.close()
            connection.close()

            return {"result": "Análise de sentimentos adicionada ao banco de dados com sucesso!"}
        else:
            prompt = prompts[keyword]
            result = run_with_fallback(prompt, text)
    else:
        logger.info("Palavra-chave não reconhecida, usando tratamento padrão.")
        result = run_gemini(f"Processe o seguinte texto: {text}", text)
    
    return {"result": result}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)