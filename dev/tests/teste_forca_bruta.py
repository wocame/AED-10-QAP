# -*- coding: utf-8 -*-

# Imports #####################################################

import matplotlib.pyplot as plt
import numpy as np

import QAPBancoAnalise.utilidades as util
from QAPBancoAnalise.QAPBanco import QAPBanco
from tests.QAPBancoTeste import QAPBancoTeste
from QAPBancoAnalise.forca_bruta import forca_bruta


repeticoes = 5
min_deps = 2
max_deps = 6
debug = 1
media = []
desvp = []

test_n = list(range(min_deps, max_deps + 1))
qaps = [QAPBanco(util.gerar_entrada_aleatoria(n)) for n in test_n]

for qap in qaps:
    print("")
    print("Problema:")
    print(qap.resgatar_dependencias())
    teste = QAPBancoTeste(qap, repeticoes)
    teste.resolver_problema_com(forca_bruta)
    print("Solucoes:")
    for rota in teste.rota_resolvido(): print("\t"+rota)
    print(f"Tempo de execução:{teste.tempo_medio()} +- {teste.tempo_desvio()} segundos")
    media.append(teste.tempo_medio())
    desvp.append(teste.tempo_desvio())

plt.plot(test_n, media, 'b', label="media")
plt.errorbar(test_n, media, desvp, linestyle='None', ecolor='r', label="desvio padrão")
plt.legend(loc='upper left')
plt.title("Tempo de execução: Força Bruta")

plt.savefig("testForcaBruta.png")
