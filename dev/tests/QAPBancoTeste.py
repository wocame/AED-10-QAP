# -*- coding: utf-8 -*-

# Imports
import numpy as np
from QAPBancoAnalise.QAPBanco import QAPBanco
from copy import copy


class QAPBancoTeste:

    def __init__(self, qap=None, repeticoes=5):
        """
        Método construtor
        :param qap: Problema a ser testado
        :type qap: class:`QAPBanco`
        :param repeticoes: Quantas vezes o problema será testado
        :type repeticoes: int
        """
        self.repeticoes = repeticoes
        self.__qap = qap
        self.__qap_solucionado = None
        self.__tempos = None

    def definir_problema(self, qap: QAPBanco):
        """
        Define o problema do banco a ser testado
        :param qap: Problema do banco
        :type qap: class:`QAPBanco`
        """
        self.__qap = qap

    def resgatar_problema(self):
        """
        Retorna o problema do banco definido
        :return: Problema do banco
        :rtype: class:`QAPBanco`
        """
        return self.__qap

    def resolver_problema_com(self, alg):
        """
        Resolve a QAP do banco com o algoritmo especificado
        :param alg: Algoritmo a ser testado
            '-> n: Número de dependências
            '-> D: Matriz de custo de deslocamento entre dependências
            '-> F: Matriz de fator de risco
            '-> Retorno: Matriz da solução
        :type alg: function(int,list,list)->list
        """

        # Zerando atributos do teste
        self.__tempos = []
        self.__qap_solucionado = []

        # Rodadas do algoritmo
        for i in range(self.repeticoes):
            self.__qap.resolver_com(alg)
            self.__qap_solucionado.append(copy(self.__qap))
            self.__tempos.append(self.__qap.tempo_execucao())

    def resolvido(self):
        """
        Informa a(s) soluçao(ões) do problema
        :returns: Problema(s) solucionados
        :rtype: list
        """
        return self.__qap_solucionado

    def tempo_resolvido(self):
        """
        Informa tempo(s) de execução do ultimo teste rodado
        :return: Tempo(s) da ultima execução em segundos
        :rtype: list
        """
        return np.array(self.__tempos)

    def tempo_medio(self):
        """
        Informa médio do tempo de execução da ultima rodada
        :return: Tempo médio de execução em segundos
        :rtype: float
        """
        return self.__tempos.mean()

    def tempo_desvio(self):
        """
        Desvio padrão do tempo de execução na ultima rodada
        :return: Desvio padrão em segundos
        :rtype: float
        """
        return self.__tempos.std()
