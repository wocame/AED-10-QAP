# -*- coding: utf-8 -*-

# Imports
import random

from QAPBanco.QAPBanco import QAPBanco
from Algoritmo.anneal import Annealer


class QAPSA(Annealer):
    """
    Extensão da classe Annealer do 'perrygeo/simanneal' para resolver a QAP com o Classical Simulated Annealing
    """

    def __init__(self, n, D, F):
        self.n = n
        self.D = D
        self.F = F
        super(QAPSA, self).__init__(list(range(n)))  # important!

    def update(self, *args, **kwargs):
        """
        Não mostrar updates
        """
        return

    def move(self):
        """
        Seleção de vizinho
        """
        a = random.randint(0, len(self.state) - 1)
        b = random.randint(0, len(self.state) - 1)
        self.state[a], self.state[b] = self.state[b], self.state[a]

    def energy(self):
        """
        Função objetivo
        """
        return QAPBanco.calculo_fator_escolha(self.n, self.D, self.F, QAPBanco.calculo_solucao_rota(self.state))


# Algoritmo
def simulated_annealing(n, D, F):
    """
    Algoritmo Simulated Annealing para calcular QAP do banco

    :param n: Número de dependências
    :param D: Matriz de custo de deslocamento entre dependências
    :param F: Matriz de fator de risco
    :return: Matriz de escolha com rota ótima
    """

    qapsa = QAPSA(n, D, F)
    rota, _ = qapsa.anneal()
    return QAPBanco.calculo_solucao_rota(rota)
