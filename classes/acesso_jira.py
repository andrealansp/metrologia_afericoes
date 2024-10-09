from __future__ import annotations

import traceback
from typing import cast, List

import jirapt
from jira import JIRA
from jira.client import ResultList
from jira.resources import Issue

import config
from classes.funcoes import Funcoes


class AcessoJira:
    def __init__(self):
        pass

    @staticmethod
    def pesquisar(jql):
        """
        Retorna a lista de dicionários com chamados do jira
        :param jql:
        :return: lista_chamados
        """
        jira = JIRA(basic_auth=(config.USER_JIRA, config.API_TOKEN),
                    server=config.SERVIDOR)

        myself = jira.myself()

        issues = cast(ResultList[Issue], jirapt.search_issues(jira, jql, 2))
        lista_chamados: List = []
        for chamado in issues:
            status = ""
            resolucao = ""
            # Verificando campos nulos:
            if chamado.fields.resolution:
                resolucao = chamado.fields.resolution.name
            if chamado.fields.status:
                status = chamado.fields.status.name

            try:
                lista_chamados.append({
                    "Utilizar Centro de Custo": f'{chamado.fields.customfield_10122.value} - '
                                                f'{chamado.fields.customfield_10122.child.value}' or "N/A",
                    "Chave": chamado.key or "N/A",
                    "Status": status or '',
                    "Abertura": chamado.fields.created,
                    "Resolução": resolucao or '',
                    "Atualizado(a)": chamado.fields.updated or " ",
                    "Responsável": chamado.fields.assignee.displayName or "N/A",
                    "Relator": chamado.fields.reporter.displayName or "N/A",
                    "Resolvido": chamado.fields.resolutiondate or " ",
                    "Data prevista para utilização": chamado.fields.customfield_10307 or " ",
                    'Lacre primário (verde, 13557S) | Quantidade:': chamado.fields.customfield_10303 or 0,
                    'Lacre secundário (azul, 14144S) | Quantidade:': chamado.fields.customfield_10304 or 0,
                    'Selo não metr. PROI (16062S) | Quantidade:': chamado.fields.customfield_10305 or 0,
                    'Selo não metr. PROD (16063S) | Quantidade:': chamado.fields.customfield_10306 or 0,
                    'Tipo de aferição': Funcoes.verfica_tipo_afericao(chamado.fields.customfield_10341) or ' ',
                    'Tipo de envio': chamado.fields.customfield_10339.value or "N/A",
                    'Solicitação de envio': Funcoes.verfica_lista_labels(chamado.fields.customfield_10213) or "N/A"
                })
            except AttributeError as e:
                print(f"Erro ao processar chamado {chamado.key}: {type(e).__name__} : - {e}")
                traceback.print_exc()
            except TypeError as e:
                print(f"Erro ao processar chamado {chamado.key}: {type(e).__name__} : - {e}")

        return lista_chamados
