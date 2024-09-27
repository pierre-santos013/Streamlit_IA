import streamlit as st
import datetime
import pymysql
from utils import function_aux as fa



connection = pymysql.connect(
    host='localhost',
    user='root',
    password='root123',
    database='basedados'
)

cursor = connection.cursor()


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




def inserir_dados_ligacao2():
    # Inserir dados das ligações
    ticket_id = st.session_state.ticket.split('ticket/')[1]
    ligparse1 = fa.ligacao()  # A função ligacao retorna a lista de dados
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
                #transcription = st.session_state.transcricao[i][0]['transcription']
                transcription = 'sem audio' if "transcription" not in st.session_state.transcricao[i] else st.session_state.transcricao[i][0]['transcription']

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

def inserir_dados_ligacao():
    # Inserir dados das ligações
    ticket_id = st.session_state.ticket.split('ticket/')[1]
    ligparse1 = fa.ligacao()  # A função ligacao retorna a lista de dados
    inserido_sucesso = False  # Variável de controle para saber se ao menos uma ligação foi inserida

    try:
        with connection.cursor() as cursor:
            i = 0
            for lig in ligparse1:
                link = lig[3]
                data_ligacao_str = lig[0]
                origem_call = lig[1]
                name_atendente = lig[2]
                data_ligacao = datetime.datetime.strptime(data_ligacao_str, '%d/%m/%Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
                
                # Verificar se a transcrição existe, se não, definir como "sem audio"
                if "detail" in st.session_state.transcricao[i]:
                    transcription = "sem audio"
                    file_path = None  # Definir file_path como None se não houver transcrição
                    file_name = "link sem audio"  # Definir file_name como None se não houver transcrição
                else:
                    transcription = st.session_state.transcricao[i][0]['transcription']
                    file_path = st.session_state.transcricao[i][0]['file_path']
                    file_name = st.session_state.transcricao[i][0]['filename']

                # Verificar se o link já existe no banco de dados
                sql_verificar = "SELECT COUNT(1) FROM ligacoes WHERE link = %s"
                cursor.execute(sql_verificar, (link,))
                resultado = cursor.fetchone()

                i += 1

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

def inserir_dados_resumo2(resumo_chat):

    ticket_id = st.session_state.ticket.split('ticket/')[1]
    if not ticket_id:
        st.toast("Resumo Chat: Ticket ID inválido!")
        return False
    try:
        with connection.cursor() as cursor:
            sql = """
            INSERT INTO tickets (resumo) where id = %s
            
            """
            cursor.execute(sql, (resumo_chat,))
            connection.commit()

            is_exist = st.toast("Dado inserido com sucesso!")
            return is_exist
    except Exception as e:
        st.toast(f"Erro ao inserir dado: {e}")
        connection.rollback()

def inserir_dados_resumo(resumo_chat):
    ticket_id = st.session_state.ticket.split('ticket/')[1]

    # Verifique se o ticket_id é válido e existe
    if not ticket_id:
        st.toast("Ticket ID inválido!")
        return False

    try:
        with connection.cursor() as cursor:
            # Verifique se o ticket_id já existe
            cursor.execute("SELECT 1 FROM tickets WHERE id = %s", (ticket_id,))

            #if cursor.fetchone():
            #    st.toast(f"Ticket com ID {ticket_id} já existe!")
            #    return False

            # Inserir dados na tabela tickets
            sql = """
            UPDATE tickets SET resumo_chat = %s WHERE id = %s
            """
            cursor.execute(sql, (resumo_chat, ticket_id))
            connection.commit()

            st.toast(f"Resumo do chat inserido com sucesso para o ticket {ticket_id}!")
            return True
    except Exception as e:
        st.toast(f"Erro ao inserir dado: {e}")
        connection.rollback()
        return False        