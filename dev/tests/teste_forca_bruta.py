# -*- coding: utf-8 -*-

# Imports #####################################################

import matplotlib.pyplot as plt
import time
import numpy

import src.utilidades as util
from src.QAPBanco import QAPBanco
from src.forca_bruta import forca_bruta


# Methods #####################################################

def testar_algoritmo(n, repeticoes, debug=0):
    # Preparar problema
    qap = QAPBanco(util.gerar_entrada_aleatoria(n))
    if debug: print("")
    if debug: print("Problema gerado:")
    if debug: print(qap.resgatar_dependencias())
    if debug: print("")
    if debug: print("Rodando algoritmo", repeticoes, "vezes...")

    # Rodadas do algoritmo
    tempos = []
    for i in range(repeticoes):
        qap.resolver_com(forca_bruta)
        tempos.append(qap.tempo_execucao())
        if debug: print("-> Tempo da rodada:", qap.tempo_execucao(), "segundos")

    # Finalizando rodadas
    if debug: print("Resultados do problema...")
    if debug: print("-> Fator de escolha:", qap.fator_escolha())
    if debug: print("-> Custo logística: ", qap.custo_logistica())
    if debug: print("-> Rota da Solução: ", qap.rota_solucao())
    return numpy.array(tempos)


# Test ########################################################

repeticoes = 5
min_deps = 2
max_deps = 7
debug = 1
media = numpy.zeros(max_deps + 1)
desvp = numpy.zeros(max_deps + 1)

test_n = list(range(min_deps, max_deps + 1))

for n in test_n:
    print("")
    print(f'Executando com n={n}...')
    tempos = testar_algoritmo(n, repeticoes, debug)

    media[n] = tempos.mean()
    desvp[n] = tempos.std()
    print(f"Tempo de execução:{media[n]} +- {desvp[n]} segundos")

plt.plot(test_n, [n * pow(2, n) / 360 for n in test_n], 'g', label="n*(2^n)")
plt.plot(test_n, media[min_deps:max_deps + 1], 'b', label="media")
plt.errorbar(test_n, media[min_deps:max_deps + 1], desvp[min_deps:max_deps + 1], linestyle='None', ecolor='r',
             label="desvio padrão")
plt.legend()

plt.savefig("testForcaBruta.png")
