from typing import List

class Funcoes:

    def __init__(self):
        pass

    @staticmethod
    def retorna_chamados_diferentes(lista1, lista2) -> List:
        """
        Retorna a diferença entra as listas de dicionários
        :param lista1:
        :param lista2:
        :return: diferença entre as listas
        """
        diferenca: List = []
        for dicionario1 in lista1:
            existe = False
            for dicionario2 in lista2:
                if dicionario1['Chave'] == dicionario2['Chave']:
                    existe = True
                    break

            if not existe:
                diferenca.append(dicionario1)

        return diferenca

    @staticmethod
    def verifica_diferenca(lista_sharepoint, lista_jira) -> List:
        """
        :param lista_sharepoint: Chamados do Share_Point
        :param lista_jira: Chamados do Jira
        :return: lista atualizada dos chamados
        """
        try:
            dicionario_auxiliar = {}
            for dicionario in lista_jira:
                chave = dicionario["Chave"]
                dicionario_auxiliar[chave] = dicionario


            for dicionario in lista_sharepoint:
                chave = dicionario["Chave"]
                if chave in dicionario_auxiliar:
                    dicionario.update(dicionario_auxiliar[chave])

        except KeyError:
            pass
        return lista_sharepoint

    @staticmethod
    def verfica_lista_labels(labels):
        if labels:
            lista_labels = ",".join(labels)
            return lista_labels
        else:
            return labels

    @staticmethod
    def verfica_tipo_afericao(tipo_afericao) -> str:
        if tipo_afericao is None:
            return "Não Selecionado"
        else:
            return tipo_afericao[0].value
