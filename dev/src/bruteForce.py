# -*- coding: utf-8 -*-
import numpy;
import geopy.distance;
from itertools import permutations
from geopy.distance import geodesic

size = 3  # tamanho da amostra. Não pode ser menor que 2.
max_range = 90  # valor de distancia máxima das localidades
custo = 10  # valor do custo
risco = []
custo_desloc = []
chance_ataque = []
# Entrada de dados aleatórios de acordo com o o solicitado
def entrada():
    global risco;
    global custo_desloc;

    # recebe o range de distância máxima em max_range e gera a quantidade de números aleatórios passados em 'size'
    latitude = numpy.random.randint(-90, max_range, size);
    longitude = numpy.random.randint(-90, max_range, size);
    # gera números aleatórios de 1 a 6
    risco = numpy.random.randint(1, 6, size);

    # Preparando dados
    # d = custo de deslocamento
    # Primeiro índice respresenta a dependência de origem.
    # Segundo índice representa a dependência de destino.
    distancia = numpy.zeros((size, size))
    custo_desloc = numpy.zeros((size, size))

    for i in range(size):
        for j in range(size):
            distancia[i][j] = geodesic((latitude[i], longitude[i]), (latitude[j], longitude[j])).km;
            custo_desloc[i][j] = custo * distancia[i][j];

    print("Distancia:")
    print(distancia)
    print(custo_desloc)

def chanceAtaque(depOrig, depDest, posicao1, posicao2):
    return risco[depDest] * posicao1;

def bruteForce():
    # Iniciando algoritmo para calcular QAP
    # Permutações
    # numpy.indentity => matriz de identidade
    permutacao = numpy.identity(size)
    print("Uma permutação:")
    print(permutacao)
    permutacoes = [numpy.array(perm) for perm in permutations(permutacao)]
    print("Permutações:")
    for perm in permutacoes:
        chance_ataque = numpy.zeros((size, size))

        # custo_desloc * chance_ataque * perm

        print(perm)







# inicializa função
entrada();


