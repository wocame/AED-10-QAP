# -*- coding: utf-8 -*-

# Imports
import numpy as np
from QAPBancoAnalise.QAPBanco import QAPBanco
from copy import copy


class QAPBancoTeste:
    """
    Teste de algoritmo para solucionar :class:`QAPBanco`
    :param repeticoes: Número de vezes para executar o algoritmo
    :param __qap: Problema a ser resolvido
    :param __qap_solucionado: Lista do(s) problema(s) solucionado(s)
    :param __repeticoes: Repeticoes usadas para solucionar o problema
    :param __alg: Algoritmo usado para solucionar o problema
    """

    def __init__(self, qap=None, repeticoes=5):
        """
        Método construtor
        :param qap: Problema a ser testado
        :param repeticoes: Quantas vezes o problema será testado
        """

        # Valores padrão
        self.repeticoes = repeticoes
        self.__qap = None
        self.__qap_solucionado = None
        self.__repeticoes = None
        self.__alg = None

        if qap is not None:
            self.definir_problema(qap)

    def definir_problema(self, qap: QAPBanco):
        """
        Define o problema do banco a ser testado
        :param qap: Problema do banco
        """
        self.__qap = qap

    def resgatar_problema(self):
        """
        Retorna o problema do banco definido
        :return: Problema do banco
        """
        return self.__qap

    def num_dependencias_problema(self):
        """
        Retorna o numero de dependencias do problema
        :return: Problema do banco
        """
        return self.__qap.num_dependencias()

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
        self.__alg = alg
        self.__repeticoes = self.repeticoes

        # Rodadas do algoritmo
        for i in range(self.repeticoes):
            self.__qap.resolver_com(alg)
            self.__qap_solucionado.append(copy(self.__qap))

    def problema_resolvido(self):
        """
        Informa a(s) soluçao(ões) do problema
        :returns: Problema(s) solucionados
        """
        return self.__qap_solucionado

    def rota_resolvido(self):
        """
        Informa a(s) rota(s) da solucao do problema
        :returns: Rota(s) encontradas
        """
        return [qap.rota_solucao() for qap in self.__qap_solucionado]

    def tempo_resolvido(self):
        """
        Informa tempo(s) de execução do ultimo teste rodado
        :return: Tempo(s) da ultima execução em segundos
        """
        return np.array([qap.tempo_execucao() for qap in self.__qap_solucionado])

    def tempo_medio(self):
        """
        Informa médio do tempo de execução da ultima rodada
        :return: Tempo médio de execução em segundos
        """
        return self.tempo_resolvido().mean()

    def tempo_desvio(self):
        """
        Desvio padrão do tempo de execução na ultima rodada
        :return: Desvio padrão em segundos
        """
        return self.tempo_resolvido().std()

    # Métodos privados ########################################

    def __str__(self):
        string = f"QAPBancoTest com {self.__qap.num_dependencias()} dependencias\n"
        if self.__alg is None:
            string += "<Não executado>"
        else:
            string += f"Algoritmo:    {self.__alg.__name__}\n"
            string += f"Repeticoes:   {self.__repeticoes}\n"
            string += f"Tempo stats:  {self.tempo_medio()} +- {self.tempo_desvio()}"
        return string
