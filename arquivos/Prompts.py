prompts = {
    "aprovar": '''
                Com base na transcrição, responda às perguntas abaixo e inclua na resposta a pergunta original, a resposta e a justificativa com trechos específicos do texto:

                {text}

                "1- FORMA DE COBRANÇA  DA EMPRESA FOI EXPLICADA FORMA CORRETA ?\n" \
                "\nresposta: .\n" \
                "\njustificativa: ." \
                "2- CLIENTE COMPREENDEU A FORMA DE COBRANÇA DA EMPRESA? \n " \
                "\nresposta: .\n" \
                "\njustificativa: ." \
                "3- O CLIENTE CONCORDA COM A DATA DO PRÉ-AGENDAMENTO (INSTALAÇÃO DA INTERNET)? \n" \
                "\nresposta: .\n" \
                "\njustificativa: ." \
                "4- FOI INFORMADO SOBRE A NECESSIDADE DE TER UM RESPONSÁVEL CADASTRADO PARA RECEBER A EQUIPE NO DIA DA INSTALAÇÃO ? \n" \
                "\nresposta: .\n" \
                "\njustificativa: ." \
                "5- FOI OFERTADO ADICIONAR O CADASTRO DE UM SEGUNDO RESPONSÁVEL ? \n" \
                "\nresposta: .\n" \
                "\njustificativa: ." \
                "6- FOI SOLICITADO ENVIO DA COORDENADA DO LOCAL DA INATALAÇÃO PELO WHATSAPP ? \n" \
                "\nresposta: .\n" \
                "\njustificativa: ." \
                "7- FOI INFORMADO SOBRE A NECESSIDADE DE APRESENTAR O DOCUMENTO COM FOTO NO DIA DA INSTALAÇÃO ? \n" \
                "\nresposta: .\n" \
                "\njustificativa: ." \
                "8- FOI INFORMADO SOBRE A NECESSIDADE DE DEVOLVER OS EQUIPAMENTOS EM CASO DE CANCELAMENTO ? \n" \
                "\nresposta: .\n" \
                "\njustificativa: ." \
                "9- FOI INFORMADO DOS MEIOS DE PAGAMENTO, RETIRADA E ENVIO DO BOLETO OU FATURA ? \n" \
                "\nresposta: .\n" \
                "\njustificativa: ." \
                "10- FOI INFORMADO FORMAS DE CONTATO COM A EMPRESA ? \n" \
                "\nresposta: .\n" \
                "\njustificativa: ." \
                "11- FOI INFORMADO SOBRE OS BENEFÍCIOS COMO SKEELO, LESTE CLUBE (SVAs) ? \n" \
                "\nresposta: .\n" \
                "\njustificativa: ." \
                "12- FOI PERGUNTADO AO CLIENTE SE ESTÁ MIGRANDO DE UM OUTRO PROVEDOR DE INTERNET ? \n" \
                "\nresposta: .\n" \
                "\njustificativa: ." \
                "13- FOI PERGUNTADO COMO O CLIENTE CONHECEU OU FICOU SABENDO DA EMPRESA ? \n" \
                "\nresposta: .\n" \
                "\njustificativa: ." \
                "14- FOI OFERTADO A VENDA LESTE MÓVEL (CHIPE DE CELULAR DA EMPRESA)? \n" \
                "\nresposta: .\n" \
                "\njustificativa: ." \
                "15- CLIENTE FOI INFORMADO SOBRE O ENVIO E CADASTRO DO OPT-IN? \n" \
                "\nresposta: .\n" \
                "\njustificativa: ." \
                "16- CLIENTE POSSUI ALGUMA RESTRIÇÃO DE HORÁRIO? \n" \
                "\nresposta: .\n" \
                "\njustificativa: ." \
                "17- CLIENTE FOI INFORMADO DA DURAÇÃO DA INSTALAÇÃO DE 1 A 2 HORAS?\n" \
                "\nresposta: .\n" \
                "\njustificativa: ." \
                "18- CLIENTE SOLICITOU PAGAMENTO EM DÉBITO AUTOMÁTICO ? \n" \
               "\nresposta: .\n" \
                "\njustificativa: ." \
                "19- ALGUMA PERGUNTA O CLIENTE REALIZOU QUE NÃO FOI RESPONDIDA? \n" \
                "\nresposta: .\n" \
                "\njustificativa: ." \
                
                sempre responda em português do Brasil
    ''',

    "resumo": '''
            "realize um resumo da interação entre o cliente e o atendente retorne com a seguinte estruetura: " \
             
            "RESUMO GERADO PELA IA_LESTE:" \
            
            "Cliente:( informar nome do cliente e  verificar se é cliente ativo ou ja foi cliente, ou deseja reativar ) .\n\n" \
            "Atendentes: (nome dos atendentes que interagiram com o cliente). \n\n " \
            "motivo do contato do cliente: (analisar detalhadamente o motivo do contato) " \n\n\
            "procedimentos realizados por cada atendente: \n\n " \
            "Resolução: (analisar se o problema foi resolvido, se não foi resolvido informar as pendências \n" \
            
            Sempre responda em <pt-br>
    ''',

    "motivo":'''

            "Por favor, informe o motivo do contato e a satisfação do cliente: " \
    
        ''',

    "aprovar2": '''
                Com base na transcrição, responda às perguntas abaixo e inclua na resposta a pergunta original, a resposta e a justificativa com trechos específicos do texto: 

                {text}

                1- FORMA DE COBRANÇA FOI EXPLICADA FORMA CORRETA?
                2- CLIENTE COMPREENDEU A FORMA DE COBRANÇA?
                3- O CLIENTE CONCORDA COM A DATA DA ATIVAÇÃO?
                4- FOI INFORMADO SOBRE A NECESSIDADE DE TER UMA PESSOA CADASTRADA PARA RECEBER A EQUIPE?
                5- FOI OFERTADO SEGUNDO RESPONSÁVEL?
                6- FOI COLETADO COORDENADA DO CLIENTE ?
                7- FOI INFORMADO SOBRE A NECESSIDADE DE APRESENTAR O DOCUMENTO COM FOTO FÍSICO NO DIA DA VISITA?
                8- FOI INFORMADO SOBRE A NECESSIDADE DE DEVOLVER OS EQUIPAMENTOS?
                9- FOI INFORMADO DOS MEIOS DE RETIRADA E ENVIO DO BOLETO?
                10- FOI INFORMADO FORMAS DE CONTATO COM A EMPRESA ?
                11- É INFORMADO OS BENEFÍCIOS DO PLANO? (SVAS)
                12- FOI SOLICITADO AO CLIENTE A COORDENADA PELO WHATSAPP ?
                13- FOI PERGUNTADO AO CLIENTE SE ESTÁ MIGRANDO DE UM OUTRO PROVEDOR, INDEPENDENTE DO VALOR DE ATIVAÇÃO?
                14- FOI PERGUNTADO COMO CONHECEU A EMPRESA ?
                15- FOI OFERTADO O LESTE MÓVEL?
                16- CLIENTE FOI INFORMADO SOBRE O OPTIN?
                17- CLIENTE POSSUI ALGUMA RESTRIÇÃO DE HORÁRIO?
                18- FOI INFORMADO SOBRE OS BENEFÍCIOS COMO SKEELO, LESTE CLUBE (SVAs)?
                19- CLIENTE FOI INFORMADO DA DURAÇÃO DA INSTALAÇÃO DE 1 A 2 HORAS?
                20- CLIENTE SOLICITOU PAGAMENTO EM DÉBITO AUTOMÁTICO?
                21- ALGUMA PERGUNTA O CLIENTE REALIZOU QUE NÃO FOI RESPONDIDA?

                Responda em português do Brasil.
    ''',

    "sentimento":'''
                "realize uma análise detalhada " \
                "dos sentimentos do cliente e do atendente expresso no texto delimitado por {}, "\
                "classifique o sentimento de cada um como: 'positivo', 'negativo' ou 'neutro'. "\
                "Identifique e liste os sentimentos dp cliente e atendente mais presentes na interação, "\
                "em sua forma mais simples e direta (palavra primitiva)" \
                "tanto explícitos quanto implícitos, e avalie a intensidade de cada sentimento somados dentro de uma escala total de 0 (zero) a 100 (cem) em porcentagem(%). "\
                "Indique quais palavras-chave na sentença contribuíram " \
                "para os sentimentos identificados. "\
                "Além disso, sugira possíveis razões para esses sentimentos "\
                "com base na conversa. Por fim, explique como você chegou " \
                "a essas conclusões. Retorne todas essas informações em português do Brasil " \
                "no seguinte formato de um objeto JSON entre 3 cráses ´´´ respeitando a estrutura abaixo para cliente e atendente: " \
                <json>
                "{" \
                    "\"role_cliente\": \"cliente\"," \
                    "\"classe_cliente\": \"classificação\"," \
                    "\"sent_cliente\": {\"sentimento\": intensidade}," \
                    "\"razoes_possiveis_cliente\": [\"string\"]," \
                    "\"explicacao_modelo_cliente\": \"string\"," \
                    "\"role_atendente\": \"atendente\"," \
                    "\"classe_atendente\": \"classificação\"," \
                    "\"sent_atendente\": {\"sentimento\": intensidade}," \
                    "\"razoes_possiveis_atendente\": [\"string\"]," \
                    "\"explicacao_modelo_atendente\": \"string\"" \
                "}"
                <json>
                retorne apenas a estrutura do json com a análise
    ''',
    
    "cancelamento": '''
                    Você é um analista de call center responsável por verificar qual foi o atendente responsável pelo cancelamento.
                    O atendente responsável é aquele que ofereceu opções para reter o cliente, manter o plano e não cancelar por último.
                    
                 '''

    # Adicione outras ações e prompts conforme necessário
}