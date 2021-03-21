# -*- coding: utf-8 -*-

# Imports #####################################################

import matplotlib.pyplot as plt
import QAPBanco.utilidades as util
from QAPBanco.QAPBanco import QAPBanco
from QAPBancoAnalise.QAPBancoTeste import QAPBancoTeste
from QAPBancoAnalise.QAPBancoSuite import QAPBancoSuite
from Algoritmo.branch_bound import branch_bound
from Algoritmo.forca_bruta import forca_bruta

# Configurações ###############################################

repeticoes = 1
min_deps = 4
max_deps = 4
funcao = branch_bound

# Parte constante #############################################

# Gerar problemas
test_n = list(range(min_deps, max_deps + 1))
qaps = [QAPBanco(util.gerar_entrada_aleatoria(n)) for n in test_n]

# Gerando suite de testes
testes = [QAPBancoTeste(qap, repeticoes) for qap in qaps]
suite = QAPBancoSuite(testes, funcao)
suite.rodar_testes()
# Resultados do teste
print(suite)
plot = suite.grafico_tempo_execucao()
plt.savefig("test_" + funcao.__name__ + ".png")

# Força bruta para comparar
suite = QAPBancoSuite(testes, forca_bruta)
suite.rodar_testes()
print("")
print(suite)
