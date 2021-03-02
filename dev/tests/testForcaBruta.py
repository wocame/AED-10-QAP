# -*- coding: utf-8 -*-

# Imports #####################################################

import sys

sys.path.append("../src")
import time
import src.utilidades as util
from src.forcaBruta import forcaBruta

# Test ########################################################

n = 6

print("")
print("Número de dependências:", n)
print("")
print("Gerando entradas aleatórias...")
G, R = util.gerarEntradaAleatoria(n)
print("")
print("Processando entradas...")
D, F = util.preparaEntrada(n, G, R)
print("")
print('Rodando força bruta...')
start = time.process_time()
X = forcaBruta(n, D, F)
tim_custo = time.process_time() - start
min_custo = util.calculoFatorEscolha(n, D, F, X)
log_custo = util.calculoCustoLogistica(n, D, X)

print("")
print("##############################")
print("### Resultados")
print("##############################")
print("")
print("Tempo de execução:", tim_custo, "segundos")
print("Min fator escolha:", min_custo)
print("Custo logistica:  ", log_custo)
print("Rota ótima:       ", end=" ")
for j in range(n):
    for i in range(n):
        if X[i][j] == 1: print(i, end=" ")
    print('->', end=" ")
for i in range(n):
    if X[i][0] == 1: print(i, end=" ")