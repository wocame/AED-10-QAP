# -*- coding: utf-8 -*-

# Imports #####################################################

import numpy
from geopy.distance import geodesic


# Methods #####################################################

# Gera dados aleatórios para o problema do banco
# Entradas:
# - n: Número de dependências
# Saídas:
# - G: Matriz de coordenadas geográficas
# - R: Matriz de Risco das entidades
def gerarEntradaAleatoria(n):
    # Geração de coordenadas geográficas aleatórias para as n dependências
    # Cada indice representa a coordenada da respectiva dependência
    latitude = numpy.random.randint(-90, 90, n)
    longitude = numpy.random.randint(-90, 90, n)
    G = numpy.column_stack((latitude, longitude))

    # Geração do Matriz de Risco das n dependências
    # Cada indice representa o risco da respectiva dependência
    R = numpy.random.randint(1, 6, n)

    return G, R


# Função Fator de Risco
# Calcula quanto a chance de ataque entre dependências em determinadas posições influencia na escolha da rota
# Entradas:
# - R: Matriz de fator de risco n por 1
# - i: indice da dependência de origem
# - j: indice da dependência de destino
# - k: posição da rota de origem
# - p: posição da rota de destino
# Saídas:
# - Fator de influencia na escolha da rota de acordo com a chance de ataque
def f(R, i, j, k, p):
    if p - k == 1:
        return 1 / (R[j] * p)
    else:
        return 0


# Função Fator de Escolha
# Calcula o fator de escolha da uma dada rota
# Entradas:
# - n: Número de dependências
# - D: Matriz de custo de deslocamento
# - F: Matriz de fator de risco
# - X: Matriz de permutação (rota)
# Saídas:
# - Fator de escolha
def calculoFatorEscolha (n, D, F, X) :
    fator_escolha = 0
    for i in range(n):
        for j in range(n):
            for k in range(n):
                for p in range(n):
                    fator_escolha += D[i][j] * F[i][j][k][p] * X[i][k] * X[j][p]
    return fator_escolha


# Função custo de logística
# Calcula o custo da logistica da uma dada rota
# Entradas:
# - n: Número de dependências
# - D: Matriz de custo de deslocamento
# - X: Matriz de permutação (rota)
# Saídas:
# - Custo de logistica
def calculoCustoLogistica (n, D, X) :
    custo_logistica = 0
    for i in range(n):
        for j in range(n):
            for k in range(n):
                for p in range(n):
                    custo_logistica += D[i][j] * X[i][k] * X[j][p]
    return custo_logistica


# Prepara dados brutos para serem usados nos algortimos
# Entradas:
# - n: Número de dependências
# - G: Matriz de coordenadas geográficas (n por 2)
# - R: Matriz de Risco das entidades (n por 1)
# Saídas:
# - D: Matriz de Custo de Deslocamento entre entidades (n por n)
# - F: Matriz de Fator de Risco (n por n por n por n)
def preparaEntrada(n, G, R):

    # V: Custo médio por quilômetro
    V = 10

    # Primeiro índice respresenta a dependência de origem.
    # Segundo índice representa a dependência de destino.
    M = numpy.zeros((n, n))
    D = numpy.zeros((n, n))
    for i in range(n):
        for j in range(n):
            # Matriz M da distancia em kilometros das dependências
            M[i][j] = geodesic(tuple(G[i]), tuple(G[j])).km

            # Matriz D de custo de deslocamento
            D[i][j] = V * M[i][j]

    # Matriz de fator de risco gerado pela função a
    F = numpy.zeros((n,n,n,n))
    for i in range(n):
        for j in range(n):
            for k in range(n):
                for p in range(n):
                    F[i][j][k][p] = f(R, i, j, k, p)

    return D, F


# Converte a matriz de permutação em uma rota mais facil de visualizar
# Entrada:
# - n: Número de dependências
# - X: Matriz de permutação com rota
# Saidas:
# - String no formato "Dep1 -> Dep2 -> ... -> DepN"
def mostrarRota(n, X):
    rota = ""
    for j in range(n):
        for i in range(n):
            if X[i][j] == 1: rota += str(i)+" "
        rota += "-> "
    for i in range(n):
        if X[i][0] == 1: rota += str(i)+" "
    return rota

# Smoke test
# n = 3
# G, R = gerarEntradaAleatoria(n)
# print("Coordenadas geográficas:")
# print(G)
# print("Risco:")
# print(R)
# D, F = preparaEntrada(n, G, R)
# print("Custo de deslocamento:")
# print(D)
# print("Fator de risco:")
# print(F)