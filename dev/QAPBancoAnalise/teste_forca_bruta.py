# -*- coding: utf-8 -*-

# Imports #####################################################

import matplotlib.pyplot as plt
import QAPBanco.utilidades as util
from QAPBanco.QAPBanco import QAPBanco
from QAPBancoAnalise.QAPBancoTeste import QAPBancoTeste
from QAPBancoAnalise.QAPBancoSuite import QAPBancoSuite
from Algoritmo.forca_bruta import forca_bruta

# Configurações ###############################################

repeticoes = 5
min_deps = 2
max_deps = 7
funcao = forca_bruta

# Parte constante #############################################

# Gerar problemas
test_n = list(range(min_deps, max_deps + 1))
qaps = [QAPBanco(util.gerar_entrada_aleatoria(n)) for n in test_n]

# Gerando suite de testes
testes = [QAPBancoTeste(qap) for qap in qaps]
suite = QAPBancoSuite(testes, funcao)
suite.rodar_testes()

# Resultados do teste
print(suite)
plot = suite.grafico_tempo_execucao()
plt.savefig("test_" + funcao.__name__ + ".png")
