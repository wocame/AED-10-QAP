# -*- coding: utf-8 -*-

# Imports #####################################################

import matplotlib.pyplot as plt
import time
import numpy
import src.utilidades as util
from src.forcaBruta import forcaBruta


# Methods #####################################################

def testForcaBruta(n, repeticoes, debug=0):
    if (debug): print("")
    if (debug): print("Número de dependências:", n)
    if (debug): print("")
    if (debug): print("Gerando entradas aleatórias...")
    G, R = util.gerarEntradaAleatoria(n)
    if (debug): print("Matriz de coordenadas (G):", [cord for cord in G])
    if (debug): print("Fator de risco (R):", R)
    if (debug): print("")
    if (debug): print("Processando entradas...")
    D, F = util.preparaEntrada(n, G, R)
    if (debug): print("Custo de deslocamento (D):")
    if (debug): print(D)
    if (debug): print("Fator de risco (F):")
    if (debug): print(F)

    if (debug): print("")
    if (debug): print("Rodando Forca Bruta", repeticoes, "vezes...")
    return numpy.array([rodarAlgoritmo(n, D, F, debug) for i in range(repeticoes)])


def rodarAlgoritmo(n, D, F, debug):
    start = time.process_time()
    X = forcaBruta(n, D, F)
    tim_custo = time.process_time() - start

    if (debug): print("-> Tempo da rodada:", tim_custo, "segundos")
    return tim_custo


# Test ########################################################

repeticoes = 5
min_deps = 2
max_deps = 7
debug = 0
media = numpy.zeros(max_deps + 1)
desvp = numpy.zeros(max_deps + 1)

test_n = list(range(min_deps, max_deps + 1))

for n in test_n:
    print("")
    print(f'Executando com n={n}...')
    tempos = testForcaBruta(n, repeticoes, debug)

    media[n] = tempos.mean()
    desvp[n] = tempos.std()
    print(f"Tempo de execução:{media[n]} +- {desvp[n]} segundos")

plt.plot(test_n, [n * pow(2, n) / 360 for n in test_n], 'g', label="n*(2^n)")
plt.plot(test_n, media[min_deps:max_deps + 1], 'b', label="media")
plt.errorbar(test_n, media[min_deps:max_deps + 1], desvp[min_deps:max_deps + 1], linestyle='None', ecolor='r',
             label="desvio padrão")
plt.legend()

plt.savefig("testForcaBruta.png")
