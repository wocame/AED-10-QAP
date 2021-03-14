# -*- coding: utf-8 -*-

# Imports #####################################################

import numpy as np
import pandas as pd


# Methods #####################################################

def gerar_entrada_aleatoria(n):
    """
    Gera dados aleatórios para o problema do banco
    :param n: Número de dependências do problema
    :type n: int
    :returns: Dataframe com dados aleatórios de 'n' dependencias
    :rtype: class:`pandas.DataFrame` com shape=(n,4)
    """

    # Gera identificadores aleatórios
    id = [f'Dep{i}' for i in range(n)]

    # Geração de coordenadas geográficas aleatórias para as n dependências
    # Cada indice representa a coordenada da respectiva dependência
    latitude = np.random.randint(-90, 90, n)
    longitude = np.random.randint(-90, 90, n)

    # Geração do Matriz de Risco das n dependências
    # Cada indice representa o risco da respectiva dependência
    R = np.random.randint(1, 6, n)

    return pd.DataFrame({'id': id, 'lat': latitude, 'lon': longitude, 'risco': R})


def gerar_entrada(path='../../dados', nome='Relação dos Pontos de Atendimento Brasilia v2.xlsx', max_dependencias=None):
    """
    Gera entradas da QAPBanco a partir da planilha de relação de pontos disponibilizada
    :param path: Path do arquivo
    :param nome: Nome do arquivo com extensão
    :param max_dependencias: Máximo numero de dependencias a serem carregadas
    :return: Dataframe com informações da QAPBanco
    """

    # Gerando dataframe do arquivo
    if nome[:-4] == '.csv':
        df = pd.read_csv(path + '/' + r"{nome}")
    else:
        df = pd.read_excel(path + '/' + nome)

    # Removendo registros excedentes
    if max_dependencias is not None:
        num_dependencias = len(df.index)
        if max_dependencias >= num_dependencias:
            return None
        else:
            df = df.drop(np.random.choice(df.index, num_dependencias - max_dependencias, replace=False))

    # Se não contiver coluna de riscos, insere com valores aleatórios
    if 'RISCO' not in df.columns:
        n = len(df.index)
        df.insert(loc=len(df.columns), column='RISCO', value=np.random.randint(1, 6, n))

    return pd.DataFrame({'id': df['PREFIXO'], 'lat': df['LATITUDE'], 'lon': df['LONGITUDE'], 'risco': df['RISCO']})


def salvar_dados(df: pd.DataFrame, path='../../dados', nome='qap'):
    """
    Salva dados em um arquivo CSV
    :param df: Dataframe com informações da QAPBanco
    :param path: Path do arquivo CSV
    :param nome: Nome do arquivo CSV
    """
    df.to_csv(path + '/' + nome + '.csv', index=False)


def recuperar_dados(path='../../dados', nome='qap'):
    """
    Recupera dados salvos em um arquivo CSV
    :param path: Path do arquivo CSV
    :param nome: Nome do arquivo CSV
    :return: Dataframe com informações da QAPBanco
    """
    return pd.read_csv(path + '/' + nome + '.csv')


# Smoke test
# n = 8
# print(gerar_entrada_aleatoria(n))
#
# salvar_dados(gerar_entrada(max_dependencias=6))
# print(recuperar_dados())
