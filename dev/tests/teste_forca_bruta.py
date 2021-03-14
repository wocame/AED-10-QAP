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
max_deps = 7
debug = 1
media = np.zeros(max_deps + 1)
desvp = np.zeros(max_deps + 1)

test_n = list(range(min_deps, max_deps + 1))
qaps = [QAPBanco(util.gerar_entrada_aleatoria(n)) for n in test_n]

for n in test_n:
    print("")
    print(f'Executando com n={n}...')
    teste = QAPBancoTeste(qaps[n], repeticoes)
    teste.resolver_problema_com(forca_bruta)
    media[n] = teste.tempo_medio()
    desvp[n] = teste.tempo_desvio()
    print(f"Tempo de execução:{media[n]} +- {desvp[n]} segundos")

plt.plot(test_n, [n * pow(2, n) / 360 for n in test_n], 'g', label="n*(2^n)")
plt.plot(test_n, media[min_deps:max_deps + 1], 'b', label="media")
plt.errorbar(test_n, media[min_deps:max_deps + 1], desvp[min_deps:max_deps + 1], linestyle='None', ecolor='r',
             label="desvio padrão")
plt.legend()

plt.savefig("testForcaBruta.png")
