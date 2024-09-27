import os
import streamlit as st 
import chromadb
from sentence_transformers import SentenceTransformer
import fitz 
from groq import Groq
#PyMuPDF leitura e extração de texto de um pdf

chroma_client = chromadb.Client()

collection_name = "texto"
collections = chroma_client.list_collections()

if collection_name in [col.name for col in collections]:
    collection = chroma_client.get_collection(collection_name)
else:
    collection= chroma_client.create_collection(name=collection_name)

model =  SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')


def embed_text(text):
    embedings = model.encode([text], convert_to_tensor=True)
    return embedings.cpu().numpy()[0]

# ler o arquivo e extrai o texto
def read_pdfs_from_directory(diretory):
    documents =[]
    for filename in os.listdir(diretory):
        if filename.endswith('.pdf'):
            filepath = os.path.join(diretory, filename)
            doc = fitz.open(filepath)
            text =""
            for page in doc:
                text += page.get_text()
            # LImpar o texto preservando a ortografia    
            cleaned_text = clean_text(text)
            documents.append((filename,cleaned_text))
    return documents

def clean_text(text):
    #remove os espaços extras e novas linhas desnecessárias
    cleaned_text =' '.join(text.split())
    return cleaned_text

#criar o chunk
def chunk_text(text, chunk_size=512):
    return [text[i:i+chunk_size] for i in range(0, len(text),chunk_size)]

#upload

def process_uploaded_file(uploaded_file):
    if uploaded_file is not None:
        doc = fitz.open(stream=uploaded_file.read(),filetype="pdf")
        text =" "
        for page in doc:
            text += page.get_text()
        cleaned_text = clean_text(text)
        return cleaned_text
    return None

# recuperador

def search_similar_documents(query, top_k=5):
    query_embedding = embed_text(query).tolist() # Convertendi o ndarray para uma lista
    results = collection.query(query_embeddings = [query_embedding], n_results=top_k)

    similar_documents = [metadata["content"] for metadata in results['metadatas'][0]]
    
    
    return similar_documents

llm = Groq(
    api_key = "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",
)
#gerador

def generate_decision(new_document, similar_documents):
    input_text = f'Documento novo:{new_document}\n\nDocuments Similares {' '.join(similar_documents)}'
    system_text = "Você é um analista de atendimento busque somente no texto as respostas para a pergunta do cliente, responda sempre em português e caso não tenha a resposta informe que não tem esse conhecimento, porém vai direcionar para uma pessoa que possui  "

    result = llm.chat.completions.create(
        messages=[
            {
                "role":"system",
                "content":system_text
            },
            {
                "role":"user",
                "content": input_text,
            }
        ],    
        model="llama3-70b-8192",
        )

    return result

st.title("Analisador de textos")

uploaded_file = st.file_uploader("faça upload de um arquivo", type=["pdf"])
query = st.text_input("Digite sua consulta")

result = None

if st.button("Consultar", key="botao1"):
    if uploaded_file is not None and query:
        doc_text = process_uploaded_file(uploaded_file)
        chunks = chunk_text(doc_text)
        for i, chunk in enumerate(chunks):
            embeddindg = embed_text(chunk).tolist()
            
            collection.add(embeddings=[embeddindg], ids=[f'uploaded_chunk_{i}'], metadatas=[{'filename': uploaded_file.name, 'content': chunk}])
            

            


        similar_docs = search_similar_documents(query)
        result = generate_decision(query, similar_docs)
        st.write(result.choices[0].message.content)   
    else:
        st.error("faça upload e digite sua pergunta.")  



# requisitos:
      