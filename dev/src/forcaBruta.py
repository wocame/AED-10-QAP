# -*- coding: utf-8 -*-

# Imports #####################################################

import numpy
import src.utilidades as util
from itertools import permutations

# Imports #####################################################

# Algoritmo Força Bruta para calcular QAP
# Entradas:
# - n: Número de dependências
# - D: Matriz (n por n) de custo de deslocamento entre dependências
# - F: Matriz (n por n por n por n) de fator de risco
# Saídas:
# - X: Matriz de escolha com rota ótima
def forcaBruta(n, D, F):

    # Gera todas as possiveis permutações x
    permutacao = [numpy.array(perm) for perm in permutations(numpy.identity(n))]

    # Calculo do fator de escolha de acordo com cada permutação
    custo_ponderado = []
    for X in permutacao:
        fator_escolha = util.calculoFatorEscolha(n, D, F, X)
        custo_ponderado = numpy.append(custo_ponderado, [fator_escolha])

    # Retorna matriz de escolha ótima
    idx = numpy.argmin(custo_ponderado)
    return permutacao[idx]
