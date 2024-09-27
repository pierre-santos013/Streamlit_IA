import streamlit as st
from utils import config  # Supondo que utils/config tenha a conexão e outras configs

# Função para limpar a sessão
def clear():
    st.session_state.chat_consulta = []
    st.session_state.history_consulta = []
    st.session_state.ticket = False
    st.session_state.CHAT = False
    st.session_state.COMUN = False
    st.rerun()  # Rerun para atualizar a interface após limpar

# Inicializando variáveis na sessão
if "chat_consulta" not in st.session_state:
    st.session_state.chat_consulta = []

if "history_consulta" not in st.session_state:
    st.session_state.history_consulta = []

if "ticket" not in st.session_state:
    st.session_state.ticket = False

if "CHAT" not in st.session_state:
    st.session_state.CHAT = False

if "COMUN" not in st.session_state:
    st.session_state.COMUN = False

# Interface de usuário
st.title("💬 Consulta tickets")

# Campo para inserir o ticketID
ticket_id = st.sidebar.text_input("Insira o ticketID", key="busca")

# Função para buscar ticket do banco de dados
def buscar_ticket_consulta(ticket_id):
    cursor = config.connection.cursor()
    sql = "SELECT chat, comunicacao FROM tickets WHERE id = %s"
    cursor.execute(sql, (ticket_id,))
    result = cursor.fetchone()
    cursor.close()
    
    if result is None:
        st.error("Ticket não encontrado. Realize um novo registro")
        return None, None
    else:
        return result[0], result[1]

# Exibindo mensagens armazenadas na sessão
for message in st.session_state.chat_consulta:
    role = "user" if message["role"] == "user" else "assistant"
    with st.chat_message(role):
        st.markdown(message['text'])

# Se houver um input no chat
if prompt_user := st.chat_input("Como posso ajudar?"):
    # Captura as opções selecionadas no multiselect
    selected_options = st.session_state.get('selected_options', [])

    # Adiciona os valores de st.session_state ao prompt baseado nas opções selecionadas
    if "COMUNICAÇÃO" in selected_options and st.session_state.COMUN:
        prompt = f"\nDados de comunicação: {st.session_state.COMUN} - {prompt_user}"

    if "CHAT" in selected_options and st.session_state.CHAT:
        prompt = f"\nDados do chat: {st.session_state.CHAT} - {prompt_user}"

    if "LIGAÇÃO" in selected_options:
        # Exemplo de inclusão de dados de ligação (modifique conforme necessário)
        prompt = "\nDados de ligação: (dados da ligação aqui - {prompt_user}"

    # Adiciona a mensagem do usuário ao estado da sessão
    st.session_state.chat_consulta.append({"role": "user", "text": prompt_user})

    st.session_state.history_consulta.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt_user)

    try:
        # Solicita uma resposta da IA
        response = config.client.chat.completions.create(
            messages=st.session_state.history_consulta,
            model="llama3-70b-8192"
        )

        response_text = response.choices[0].message.content

        # Exibe a resposta da IA no chat
        with st.chat_message("assistant"):
            st.write("IA-Groq:")
            st.markdown(response_text)

        # Atualiza o estado da sessão com a resposta
        st.session_state.chat_consulta.append({"role": "assistant", "text": response_text})
        st.session_state.history_consulta.append({"role": "assistant", "content": response_text})

    except Exception as e:
        # Em caso de erro, tenta fallback para Gemini
        try:
            response = config.model_g.generate_content(f"{st.session_state.history_consulta} -{prompt}")
            response_text = response.text

        except Exception as gemini_error:
            response_text = "Desculpe, ocorreu um erro ao processar sua solicitação."

        # Exibe fallback response
        with st.chat_message("assistant"):
            st.write("IA-Gemini:")
            st.markdown(response_text)

        # Atualiza o estado da sessão com a resposta fallback
        st.session_state.chat_consulta.append({"role": "assistant", "text": response_text})
        st.session_state.history_consulta.append({"role": "assistant", "content": response_text})

# Botão para buscar ticket
if st.sidebar.button("buscar ticket"):
    chat, comunicacao = buscar_ticket_consulta(ticket_id)
    if chat is not None and comunicacao is not None:
        st.session_state.ticket = True
        st.session_state.CHAT = chat
        st.session_state.COMUN = comunicacao

# Botão para limpar o histórico
if st.sidebar.button('limpar'):
    clear()

# Opções para dados adicionais
if st.session_state.ticket:
    selected_options = st.sidebar.multiselect("Selecione os dados para o chat", ("CHAT", "LIGAÇÃO", "COMUNICAÇÃO"))
    # Armazena as opções selecionadas na sessão
    st.session_state.selected_options = selected_options
