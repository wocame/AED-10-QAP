# -*- coding: utf-8 -*-

# Imports #####################################################

import numpy
import geopy.distance
from itertools import permutations
from geopy.distance import geodesic

# Imports #####################################################

size = 3  # tamanho da amostra. Não pode ser menor que 2.
max_range = 90  # valor de distancia máxima das localidades
custo = 10  # valor do custo
risco = []
custo_desloc = []
chance_ataque = []


# Methods #####################################################

# Entrada de dados aleatórios de acordo com o o solicitado
def entrada():
    global risco
    global custo_desloc

    # Geração de coordenadas geográficas aleatórias para as n dependências
    # Cada indice representa a coordenada da respectiva dependência
    latitude = numpy.random.randint(-90, max_range, size)
    longitude = numpy.random.randint(-90, max_range, size)

    # Geração do Matriz de Risco das n dependências
    # Cada indice representa o risco da respectiva dependência
    risco = numpy.random.randint(1, 6, size)

    # Preparando dados

    # Geração da matriz D de custo de deslocamento
    # Primeiro índice respresenta a dependência de origem.
    # Segundo índice representa a dependência de destino.
    distancia = numpy.zeros((size, size))
    custo_desloc = numpy.zeros((size, size))

    for i in range(size):
        for j in range(size):
            distancia[i][j] = geodesic((latitude[i], longitude[i]), (latitude[j], longitude[j])).km
            custo_desloc[i][j] = custo * distancia[i][j]

    # Matriz de fator de risco gerado pela função a
    # To do


# Função Fator de Risco
# Calcula quanto a chance de ataque entre dependências em determinadas posições influencia na escolha da rota
# Entradas:
# - i: indice da dependência de origem
# - j: indice da dependência de destino
# - k: posição da rota de origem
# - p: posição da rota de destino
# Saídas:
# - Fator de influencia na escolha da rota de acordo com a chance de ataque
def f(i, j, k, p):
    if k - p == 1:
        return 1 / (risco[j] * k)
    else:
        return 0


# Algoritmo Força Bruta para calcular QAP
# Entradas:
# - n: Número de dependências
# - R: Matriz (n por 1) de riscos das n dependências
# - D: Matriz (n por n) de custo de deslocamento entre dependências
# Saídas:
# - Matriz de escolha com rota ótima
def forcaBruta(n, R, D):

    # Gera todas as possiveis permutações x
    permutacao = [numpy.array(perm) for perm in permutations(numpy.identity(n))]

    # Calculo do fator de escolha de acordo com cada permutação
    custo_ponderado = []
    for X in permutacao:
        fator_escolha = 0
        for i in range(n):
            for j in range(n):
                for k in range(n):
                    for p in range(n):
                        fator_escolha += D[i][j] * f(i, j, k, p) * X[i][k] * X[j][p]
        custo_ponderado = numpy.append(custo_ponderado, [fator_escolha])

    # Mostrando resultados
    for idx in range(len(permutacao)):
        print("Rota:")
        print(permutacao[idx])
        print("Fator de escolha:", custo_ponderado[idx])

    # Definindo caminho ótimo
    min_idx = numpy.argmin(custo_ponderado)
    print("")
    print("Custo ponderado do caminho ótimo:", custo_ponderado[min_idx])
    print("Caminho ótimo é:")
    print(permutacao[min_idx])

# Execution ###################################################

print("Gerando entradas...")
entrada()
print("")
print("Número de dependências:", size)
print("Matriz de Riscos (R):")
print(risco)
print("Matriz de Custo de Deslocamento (D):")
print(custo_desloc)
print("")
print("Rodando força bruta...")
forcaBruta(size, risco, custo_desloc)
