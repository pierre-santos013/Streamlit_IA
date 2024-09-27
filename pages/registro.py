import streamlit as st
from utils import function_aux as fa
from utils import functions_bd as fb
from utils import config 
import os
import json
import streamlit as st
import os

st.set_page_config(
    layout='wide'
)
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

    st.title("Adicionar registros.")
    
#Somente exibe o campo de input e o botão de conversão se não houver texto convertido
    input_text = st.text_area("Cole o texto do ticket aqui", value=st.session_state.input_text)
    
    
    #col1, col2 = st.columns(2, vertical_alignment="bottom")
    col1, col2 = st.columns([1, 11])
    if col1.button("Converter"):

        if input_text:
            parsed_data = fa.dividir_texto(input_text)
            json_result = fa.criar_json(parsed_data)
            json_result = json.loads(json_result)

        # Atualizar session_state com os valores convertidos
            st.session_state.input_text = input_text
            st.session_state.chat = json_result['Interação Chat']
            st.session_state.comun = json_result['Comunicação']
            st.session_state.ticket = str(json_result['Ticket']).split("t:")[1] if "t:" in json_result['Ticket'] else json_result['Ticket']
            st.session_state.calls = json_result['Ligações']
                    
        else:
            st.warning("Por favor, cole o texto antes de converter.")
    
  
    if col2.button("salvar dados no banco"):
        fb.inserir_dados_ticket()
        fb.inserir_dados_ligacao()
    
    st.divider()
# Só exibir os valores armazenados após a conversão
    if st.session_state.input_text:
        st.session_state.show_results = True
        if st.sidebar.button("Nova Análise", type="primary"):
            fa.limpar_chat()
        #st.sidebar.divider()    

    # Exibir os resultados
        st.header("Análise do atendimento")

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
                link_call = fa.get_calls(st.session_state.calls) # tras somente as chamadas 
                st.write(f'Total de chamadas: {len(link_call)}')
                dados_call = fa.get_chamada(st.session_state.calls)
                st.session_state.dados_call = dados_call
                st.write(dados_call)
                dados_geral= st.empty()
                #st.write(link_call)
                
        
        if st.session_state.transcricao:
            
            with st.expander("Transcrição"):          
                for item in st.session_state.transcricao:
                    st.write(st.session_state.transcricao[0])     
                    
                    if "transcription" not in list(item)[0]: 
                        st.write('sem audio')                                          
                    else: 
                        st.write(f'teste: {item[0]['transcription']}')

                #with dados_geral.container():        
                #    st.write(f'teste: {item[0]['transcription']}')
                    


    # Exibir o botões de analise        
        if st.session_state.chat == "":
            pass
        else:
            if st.sidebar.button("Resumo Chat"): 
                keyword= "resumo"    
                response = fa.make_api_request(keyword, st.session_state.chat)
                resumo = response["result"]
                
                st.markdown(f"Resumo da interação: \n\n {response["result"]}")
                
                fb.inserir_dados_resumo(resumo)

        if st.sidebar.button("Análise de sentimento"): 
            keyword= "sentimento"
            if st.session_state.chat:
                with st.spinner(f"Analisando a Interação..."):
                    response = fa.make_api_request(keyword, st.session_state.chat)
                    st.markdown(f"Sentimentos Interação: \n\n {response["result"]}")  
            if not st.session_state.transcricao:
                st.write("necessário realizar a transcrição antes da análise")
            else:
                sent_transcription= st.session_state.transcricao   
                response = fa.make_api_request(keyword, sent_transcription)
                pass

        if st.sidebar.button("Análise de venda"): 
            keyword= "aprovar"
            
            venda = st.session_state.comun + st.session_state.chat 
            response = fa.make_api_request(keyword, venda)
            st.markdown(f"Análise de venda \n\n {response["result"]}")      

        if st.sidebar.button("Análise do comentário"): 
            keyword= "subtipo_venda"
            response = fa.make_api_request(keyword, st.session_state.chat)
            #st.markdown(f"Análise de venda \n\n {response["result"]}")
            st.markdown(f"Análise de venda \n\n {response}")

        if st.sidebar.button("Análise de cancelamento"): 
            keyword="abcde"
            response = fa.make_api_request(keyword, st.session_state.chat)

            #st.markdown(f"Análise de cancelamento \n\n {response['result']}")
            if 'result' in response:
                st.markdown(f"Análise de cancelamento \n\n {response['result']}")
            else:  
                st.markdown(f"Análise de cancelamento \n\n {response['detail']}")  
        
        if st.sidebar.button('Transcrever chamadas'):
            #save_folder = r'C:\\Users\\Azevedo Cobretti\\OneDrive\\Documentos\\BD_audios\\audio2'
            save_folder = r'C:\\Users\\Pierre_santos\\Documents\\Projetos\\audio2'
            if not os.path.exists(save_folder):
                os.makedirs(save_folder)

            name_link = st.session_state.ticket.split("t/")[1]
            transcricoes = []
            with st.spinner(f"Baixando {len(link_call)} arquivos..."):
                for idx, lin in enumerate(link_call):
                    
                    file_name = os.path.join(save_folder, f"{name_link}_{idx + 1}.gsm")

                    if fa.download_file(lin, file_name):
                        st.toast(f"Arquivo {idx + 1} baixado com sucesso!")
                        
                        #tentar transcrever o arquivo e armazenar 
                        with st.spinner(f"realizando a transcrição do arquivo {idx + 1} "):
                            
                            response = fa.make_api_trascription(file_name)                          
                            
                            transcricoes.append(response)
                            
                    else:
                        st.error(f"Falha ao baixar o arquivo {idx + 1}.")

            
            st.session_state.transcricao = transcricoes

        if st.sidebar.button("Relatótrio"): 
            keyword= "resumo2"
            if st.session_state.chat:
                with st.spinner(f"Analisando a Interação..."):
                    prompt= f'1- interação do chat:{st.session_state.chat}; 2- comentário e documentação: {st.session_state.comun}'
                    st.write({type(prompt)})
                    response = fa.make_api_request(keyword, prompt)
                    st.markdown(f"{response["result"]}") 
            else:
                with st.spinner(f"Analisando a chamada..."):
                    rel_transcription = []
                    for item in st.session_state.transcricao: 
                    
                        if "transcription" not in list(item)[0]: 
                            pass                                        
                        else: 
                            relatorio_call = f'teste: {item[0]['transcription']}'
                            rel_transcription.append(relatorio_call)

                    rel_call =''.join(rel_transcription)
                    prompt= f'1- Transcrição da ligação:{rel_call}; 2- comentário ou registro na documentação: {st.session_state.comun}'
                    response = fa.make_api_request(keyword, prompt)
                    st.markdown(f"{response["result"]}") 
                    
            #if not st.session_state.transcricao:
            #    st.write("necessário realizar a transcrição antes da análise")      



       
        


































if __name__ == '__main__':
    main()
