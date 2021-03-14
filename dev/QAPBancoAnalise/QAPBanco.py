# -*- coding: utf-8 -*-

# Imports
import time
import pandas as pd
import numpy as np
from geopy.distance import geodesic


class QAPBanco:
    """
    Problema de Assinalamento Quadrático de manutenção de segurança do banco
    :param n: Número de dependências do problema
    :type n: int
    :param V: Custo médio em reais por quilômetro, defaults to 10
    :type V: float
    :param f: Função de fator de risco, defaults to __fator_risco
    :type f:  function(int,int,int,int)->float
    :param id: Identificação das dependências
    :type id: list de strings com shape=(n,)
    :param G: Matriz de coordenadas geográficas das entidades
    :type G: list de tuplas (float,float) com shape=(n,)
    :param R: Matriz de Risco das entidades
    :type R: list de ints de 1 a 6 com shape=(n,)
    :param __n: Valor do atributo n usado no calculo das matrizes __D e __F
    :type __n: int
    :param __V: Valor do atributo V usado no calculo das matrizes __D e __F
    :type __V: float
    :param __f: Função f usada no calculo das matrizes __D e __F
    :type __f:  function(int,int,int,int)->float
    :param __G: Valor do atributo G usado no calculo das matrizes __D e __F
    :type __G: list de floats com shape=(n,)
    :param __R: Valor do atributo R usado no calculo das matrizes __D e __F
    :type __R: list de ints de 1 a 6 com shape=(n,)
    :param __D: Matriz de Custo de Deslocamento entre entidades
    :type __D: list de floats com shape=(n,n)
    :param __F: Matriz de Fator de Risco com todas as combinações possíveis
    :type __F: list de floats com shape=(n,n,n,n)
    :param __X: Matriz de solução (rota) do problema
    :type __X: list de booleanos com shape=(n,n)
    :param __tempo_exec: Tempo de execução em segundos do ultimo algoritmo usado para solucionar o problema
    :type __tempo_exec: float
    """

    def __init__(self, df=None):
        """
        Método construtor
        :param df: Informações das dependências, defaults to None
            '-> Col 1: Identificador
            '-> Col 2: Latitude
            '-> Col 3: Longitude
            '-> Col 4: Risco
        :type df: class:`pandas.Dataframe` com shape=(n,4)
        """

        # Valores padrão
        self.n = None
        self.V = 10
        self.f = self.__fator_risco
        self.id = None
        self.G = None
        self.R = None
        self.__n = None
        self.__V = None
        self.__f = None
        self.__G = None
        self.__R = None
        self.__D = None
        self.__F = None
        self.__X = None
        self.__tempo_exec = None

        # Se dataframe foi entrado, processa
        if df is not None:
            self.registrar_dependencias(df)

    def registrar_dependencias(self, df: pd.DataFrame):
        """
        Registra as informações das dependêcias nessa QAP
        :param df: Informações das dependências
            '-> Col 1: Identificador
            '-> Col 2: Latitude
            '-> Col 3: Longitude
            '-> Col 4: Risco
        :type df: class:`pandas.Dataframe` com shape=(n,4)
        :raises: class:`TypeError`: Dataframe entrada não está no formato correto
        """

        # Registrando número de dependências
        n = df.shape[0]

        # Checagem de dados
        if df.shape != (n, 4):
            raise TypeError(f'Exceção de entrada: Dataframe com formato {df.shape} ao inves de ({n},3)')

        # Obtendo dados dados das dependências
        self.n = n
        self.id = list(df.iloc[:, 0])
        self.G = np.column_stack((np.array(df.iloc[:, 1]), np.array(df.iloc[:, 2])))
        self.R = np.array(df.iloc[:, 3])
        self.__calcula_matrizes()

    def resgatar_dependencias(self):
        """
        Resgata dados registrados das dependências
        :returns: Informações das dependências
            '-> 'id':    Identificador
            '-> 'lat':   Latitude
            '-> 'lon':   Longitude
            '-> 'risco': Risco
        :rtype: class:`pandas.DataFrame`
        """
        return pd.DataFrame({'id': self.id, 'lat': self.G[:, 0], 'lon': self.G[:, 1], 'risco': self.R})

    def resolver_com(self, alg):
        """
        Soluciona o problema com o algoritmo fornecido
        :param alg: Função que implementa um algoritmo
        :type alg: function(
        :returns: Matriz da rota que soluciona o problema (ou None se não tiver sido solucionada)
        :rtype: class:`numpy.array com shape=(n,n)`
        """
        inicio = time.process_time()
        self.__X = alg(self.n, self.__D, self.__F)
        self.__tempo_exec = time.process_time() - inicio

    def solucao(self):
        """
        Informa a soluçao do problema
        :returns: Matriz da rota que soluciona o problema (ou None se não tiver sido solucionada)
        :rtype: class:`numpy.array com shape=(n,n)`
        """
        return self.__X

    def rota_solucao(self):
        """
        Converte a matriz de solucao em uma rota mais facil de visualizar
        :param n: Número de dependências do problema
        :type n: int
        :param X: Matriz da rota a ser convertida em rota
        :type X: numpy.array com shape=(n,n)
        :returns: Rota no formato "Dep1 -> Dep2 -> ... -> DepN -> Dep1"
        :rtype: str
        """

        rota = ""
        if self.__X is not None:
            for j in range(self.__n):
                for i in range(self.__n):
                    if self.__X[i][j] == 1: rota += self.id[i] + " "
                rota += "-> "
            for i in range(self.__n):
                if self.__X[i][0] == 1: rota += self.id[i] + " "
        return rota

    def fator_escolha(self):
        """
        Fator de escolha (custo ponderado com risco) da rota da solução
        :returns: Fator de escolha
        :rtype: float
        """
        return QAPBanco.calculo_fator_escolha(self.__n, self.__D, self.__F, self.__X)

    def custo_logistica(self):
        """
        Custo da logística da rota da solução
        :returns: Custo logístico
        :rtype: float
        """
        return QAPBanco.calculo_custo_logistica(self.__n, self.__D, self.__X)

    def tempo_execucao(self):
        """
        Tempo de execução da ultima resolução do problema
        :returns: Tempo de execução em segundos
        :rtype: float
        """
        return self.__tempo_exec

    @staticmethod
    def calculo_fator_escolha(n, D, F, X):
        """
        Fator de escolha (custo ponderado com risco) da rota fornecida
        :param n: Número de dependências do problema
        :type n: int
        :param D: Matriz de custo de deslocamento
        :type D: numpy.array com shape=(n,n)
        :param F: Matriz de Fator de Risco com todas as combinações possíveis
        :type F: numpy.array com shape=(n,n,n,n)
        :param X: Matriz da rota a ser avaliada
        :type X: numpy.array com shape=(n,n)
        :returns: Fator de escolha
        :rtype: float
        """
        fator_escolha = 0
        for i in range(n):
            for j in range(n):
                for k in range(n):
                    for p in range(n):
                        fator_escolha += D[i][j] * F[i][j][k][p] * X[i][k] * X[j][p]
        return fator_escolha

    @staticmethod
    def calculo_custo_logistica(n, D, X):
        """
        Custo da logística da rota fornecida
        :param n: Número de dependências do problema
        :type n: int
        :param D: Matriz de custo de deslocamento
        :type D: numpy.array com shape=(n,n)
        :param X: Matriz da rota a ser avaliada
        :type X: numpy.array com shape=(n,n)
        :returns: Custo logístico
        :rtype: float
        """
        custo_logistica = 0
        for i in range(n):
            for j in range(n):
                for k in range(n):
                    for p in range(n):
                        custo_logistica += D[i][j] * X[i][k] * X[j][p]
        return custo_logistica


    # Métodos privados ########################################

    def __calcula_matrizes(self):
        """
        Gera as matrizes necessárias para realização do calculo da solução
        """

        # Verifica se é realmente necessário recalcular as matrizes
        if self.__V == self.V and self.__f == self.f and self.__G == self.G and self.__R == self.R:
            return

        # Primeiro índice respresenta a dependência de origem.
        # Segundo índice representa a dependência de destino.
        M = np.zeros((self.n, self.n))
        D = np.zeros((self.n, self.n))
        for i in range(self.n):
            for j in range(self.n):
                # Matriz M da distancia em kilometros das dependências
                M[i][j] = geodesic(tuple(self.G[i]), tuple(self.G[j])).km

                # Matriz D de custo de deslocamento
                D[i][j] = self.V * M[i][j]

        # Matriz de fator de risco gerado pela função a
        F = np.zeros((self.n, self.n, self.n, self.n))
        for i in range(self.n):
            for j in range(self.n):
                for k in range(self.n):
                    for p in range(self.n):
                        F[i][j][k][p] = self.f(i, j, k, p)

        # Registrando matrizes calculadas
        self.__n = self.n
        self.__V = self.V
        self.__f = self.f
        self.__G = self.G
        self.__R = self.R
        self.__D = D
        self.__F = F

    def __fator_risco(self, i, j, k, p):
        """
        Função Fator de Risco padrão.
        Calcula a influencia na escolha do trajeto devido a chance de ataque entre dependências
        em determinadas posições da rota
        :param i: indice da dependência de origem
        :type i: int
        :param j: indice da dependência de destino
        :type j: int
        :param k: posição da rota de origem
        :type k: int
        :param p: posição da rota de destino
        :type p: int
        :returns: Fator de risco
        :rtype: float
        """
        if p - k == 1:
            return 1 / (self.R[j] * p)
        else:
            return 0

    def __copy__(self):
        obj = QAPBanco()
        obj.n = self.n
        obj.V = self.V
        obj.f = self.f
        obj.id = self.id
        obj.G = self.G
        obj.R = self.R
        obj.__n = self.__n
        obj.__V = self.__V
        obj.__f = self.__f
        obj.__G = self.__G
        obj.__R = self.__R
        obj.__D = self.__D
        obj.__F = self.__F
        obj.__X = self.__X
        obj.__tempo_exec = self.__tempo_exec
        return obj
