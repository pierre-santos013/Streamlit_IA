
import streamlit as st
from groq import Groq
import google.generativeai as genai
import assemblyai as aai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
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
