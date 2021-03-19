# -*- coding: utf-8 -*-

# Imports
from QAPBanco.QAPBanco import QAPBanco
from scipy.optimize import dual_annealing


# Função objetivo adaptada do QAP para Simulated Annealing
def delta(n, D, F, rota):
    return QAPBanco.calculo_fator_escolha(n, D, F, QAPBanco.calculo_solucao_rota(rota))


# Algoritmo
def simulated_annealing(n, D, F):
    """
    Algoritmo Simulated Annealing para calcular QAP do banco
    :param n: Número de dependências
    :param D: Matriz de custo de deslocamento entre dependências
    :param F: Matriz de fator de risco
    :return: Matriz de escolha com rota ótima
    """

    lb = [0] * n
    ub = [n-1] * n
    res = dual_annealing(func=lambda x: delta(n, D, F, x),
                         bounds=list(zip(lb, ub)),
                         no_local_search=True)
    return QAPBanco.calculo_solucao_rota(res.x)
