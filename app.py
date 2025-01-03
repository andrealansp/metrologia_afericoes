"""
Autor: André Alan Alves

Colossenses 3:2-5
Pensai nas coisas lá do alto, não nas que são aqui da terra; porque morrestes,
e a vossa vida está oculta juntamente com Cristo, em Deus.
Quando Cristo, que é a nossa vida, se manifestar, então,
vós também sereis manifestados com ele, em glória. Fazei,
pois, morrer a vossa natureza terrena: prostituição,
impureza, paixão lasciva, desejo maligno e a avareza, que é idolatria



Projeto realizado para integrar JIRA + SHAREPOINT + POWER APPS
"""
import logging
import time
import traceback
from typing import List

import shareplum
from shareplum import Office365
from shareplum.site import Version

from config import *
from classes.acesso_jira import AcessoJira
from classes.funcoes import Funcoes
from classes.emailsender import Emailer

logger = logging.getLogger(__name__)
logging.basicConfig(filename='app.log', format='%(asctime)s - %(levelname)s: %(message)s', encoding='utf-8',
                    level=logging.INFO)

tempo_inicial = time.time()
# Carregar Lista do SharePoint, após essa carga utilizo a lista para verificar quais chamados da lista do sharepoint
# não está na lista do JIRA.
try:
    authcookie = Office365(
        SHAREPOINT, username=USUARIO_365, password=SENHA
    ).GetCookies()
    sharepoint_site = shareplum.Site(
        SHAREPOINT_SITE, version=Version.v365, authcookie=authcookie
    )
    lista_sharepoint = sharepoint_site.List("Saída de Lacres - Jira")
    dados_lista_sharepoint: List = lista_sharepoint.get_list_items("Todos os Itens")
except Exception as e:
    print(traceback.format_exc())
    print("Favor verificar usuário e senha ! - " + e.args[1])
    exit()

# Carregar chamados do JIRA, após esse carga do Jira utilizo a classe Funções para verificar quais chamados do jira
# Não está na lista do sharepoint.
dados_jira: List = AcessoJira.pesquisar(JQL)
# rotina para verificar a diferença entre as listas do sharepoint e jira .
func = Funcoes()
diferenca_chamados_jira = func.retorna_chamados_diferentes(
    dados_jira, dados_lista_sharepoint
)
diferenca_chamados_sp = func.retorna_chamados_diferentes(
    dados_lista_sharepoint, dados_jira
)
# Quando há a diferença no jira, criamos os chamados.
try:
    if diferenca_chamados_jira:
        lista_sharepoint.UpdateListItems(data=diferenca_chamados_jira, kind="New")
        logger.info(f"Chamados Adicionados: {len(diferenca_chamados_jira)}")
    else:
        logger.info("Sem chamados para adicionar !")
except Exception as e:
    print(f"Erro ao interagir com o SharePoint - Adição: {e}")

try:
    if diferenca_chamados_sp:
        lista_ids_delete: List = []
        for chamado_a_excluir in diferenca_chamados_sp:
            lista_ids_delete.append(chamado_a_excluir["ID"])
        lista_sharepoint.update_list_items(data=lista_ids_delete, kind="Delete")
        logger.info(f"Chamados Excluidos: {len(lista_ids_delete)}")
    else:
        logger.info(f"Sem chamados para excluir")
except Exception as e:
    print(f"Erro ao interagir com o SharePoint: {e}")

# Carrega o novo status da Lista do share point, compara com a lista do Jira e atualiza
try:
    dados_atualizados_sharepoint = sharepoint_site.List("Saída de Lacres - Jira")
    lista_atualizada_sharepoint: List = lista_sharepoint.get_list_items(
        "Todos os Itens"
    )
    atualizacao_chamados: List = func.verifica_diferenca(
        lista_atualizada_sharepoint, dados_jira
    )
    dados_atualizados_sharepoint.update_list_items(
        data=atualizacao_chamados, kind="Update"
    )
    logger.info(f"Chamados atualizados. {len(atualizacao_chamados)}")
except Exception as e:
    print("Erro", e.__str__())

# Contabiliza o tempo de execução do script
tempo_final = time.time()
tempo = tempo_final - tempo_inicial
email = Emailer(DADOS_EMAIL[0], DADOS_EMAIL[1])

# Rotina para envio do e-mail
mensagem = f"""
O script de atualização da lista "Saída de Lacres - Jira" foi executado com sucesso.
Tempo de Execução: {tempo}
"""

email.definir_conteudo(
    topico="Atualizador Executado Com Sucesso ",
    email_remetente="andre@andrealves.eng.br",
    lista_contatos=LISTA_CONTATOS,
    conteudo_email=mensagem,
)

email.enviar_email(intervalo_em_segundos=5)
