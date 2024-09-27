import streamlit as st
import pymysql
from pydub import AudioSegment
from pydub.playback import play
from utils import config


st.set_page_config(
    layout='wide'
)

# funções
def buscar_ticket(ticket_id):
    cursor = config.connection.cursor()
    sql = "SELECT id, comunicacao, chat, resumo_chat FROM tickets WHERE id = %s"
    cursor.execute(sql, (ticket_id,))

    result = cursor.fetchone()        
        
    if result is None:
            st.error("Ticket não encontrado. Realize um novo registro")
            st.switch_page("pages/registro.py")         
    else:
        CHAT = [result[2]]
        CHAT_RESUMO = [result[3]]
        COMUNICATION = [result[1]]

        # Feche a conexão
        cursor.close()
        config.connection.close()
    return COMUNICATION, CHAT, CHAT_RESUMO

# origem_call, data_ligacao, name_atendente, transcricao, filepath

def buscar_ligacao(ticket_id):
    cursor = config.connection.cursor()
    sql = "SELECT data_ligacao, origem_call, name_atendente, transcricao, filepath  FROM ligacoes WHERE ticket_id = %s"
    cursor.execute(sql, (ticket_id,))
    result_l = cursor.fetchone()  

    if result_l is None:
        st.toast("Ticket não posui Ligações")               
    else:
        DATA_CALL = result_l[0]
        ORIGEM_CALL = result_l[1]
        NAME_ATENDENTE = result_l[2]
        TRANSCRICAO = result_l[3] 
        FILEPATH = result_l[4]

        # Fechar a conexão
        cursor.close()
        config.connection.close()
        return DATA_CALL, ORIGEM_CALL, NAME_ATENDENTE, TRANSCRICAO, FILEPATH



st.title("Consulta Atendimento")
input_ticket = st.sidebar.text_input("Insira o ticketID")

if "ticket_data" not in st.session_state:
    st.session_state.ticket_data = None

ticket_id = input_ticket


if st.sidebar.button("buscar ticket"):
    #st.session_state.buscar_ticket =True
    st.session_state.ticket_data = buscar_ticket(ticket_id)
    if st.session_state.ticket_data:
        result_ticket = st.session_state.ticket_data         

        st.markdown(f"#### TICKET:  https://sosbeta.lestetelecom.com.br/ticket/{ticket_id}")
                
        col1, col2 = st.columns(2)
                
        with col1:
            tab1, tab2, tab3 = st.tabs(["CHAT", "RESUMO-CHAT", "COMUNICAÇÃO"])
            with tab1:
                with st.container(border=True):
                    with st.expander("CHAT"):
                        st.write(result_ticket[1][0])           
            with tab2:
                with st.container(border=True): 
                    with st.expander("RESUMO-CHAT"):
                        st.write(result_ticket[2][0])
            with tab3:
                with st.container(border=True):
                    with st.expander("RESUMO-CHAT"):
                        st.markdown(result_ticket[0][0])

        with col2:
            pass


    

            

    

