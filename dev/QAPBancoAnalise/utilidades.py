# -*- coding: utf-8 -*-

# Imports #####################################################

import numpy
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
    latitude = numpy.random.randint(-90, 90, n)
    longitude = numpy.random.randint(-90, 90, n)

    # Geração do Matriz de Risco das n dependências
    # Cada indice representa o risco da respectiva dependência
    R = numpy.random.randint(1, 6, n)

    return pd.DataFrame({'id': id, 'lat': latitude, 'lon': longitude, 'risco': R})


# Smoke test
# n = 8
# print(gerar_entrada_aleatoria(n))
