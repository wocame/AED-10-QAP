# -*- coding: utf-8 -*-

# Imports
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class QAPBancoSuite:
    """
    Suite de testes de problemas do banco

    :param __alg: Algoritmo usado pelos testes
    :param __testes: Testes a serem rodados
    :param __testes_executados: Testes que foram rodados
    """

    def __init__(self, testes=None, alg=None):
        """
        Método construtor

        :param testes: Testes da suite
        :param alg: Algoritmo para executar os testes
        """

        # Valores padrão
        self.__alg = None
        self.__testes = None
        self.__testes_executados = None

        if alg is not None:
            self.definir_algoritmo(alg)

        if testes is not None:
            self.definir_testes(testes)

    def definir_testes(self, testes):
        """
        Define testes a serem executados

        :param testes: Lista de testes
        """
        self.__testes = testes
        self.__testes_executados = None

    def resgatar_testes(self):
        """
        Recupera testes definidos

        :return: Lista de testes
        """
        return self.__testes

    def definir_algoritmo(self, alg):
        """
        Define algoritmo para executar os testes

        :param alg: Algoritmo
        """
        self.__alg = alg
        self.__testes_executados = None

    def resgatar_algoritmo(self):
        """
        Recupera algoritmo para executar os testes

        :return: Algoritmo
        """
        return self.__alg

    def rodar_testes(self):
        """
        Executa os testes definidos
        """
        for teste in self.__testes:
            teste.resolver_problema_com(self.__alg)
        self.__testes_executados = self.__testes

    def testes_executados(self):
        """
        Resgata testes que foram executados

        :return: Lista de testes
        """
        return self.__testes_executados

    def dados_tempo_execucao(self):
        """
        Gera dados relacionados ao tempo de execução dos testes

        :return: Dataframe com número de dependencias, média e desvio
        """

        # Garante que foi executado
        if self.__testes_executados is None:
            return None

        # Define valores de 'n' testados
        valores_n = []
        teste_n = {}
        for teste in self.__testes_executados:
            n = teste.num_dependencias_problema()
            if n not in teste_n:
                teste_n[n] = [teste]
                valores_n.append(n)
            else:
                teste_n[n].append(teste)
        valores_n.sort()

        # Obter info de tempo de execucao
        media = []
        stdev = []
        for n in valores_n:
            media_n = []
            stdev_n = []
            for teste in teste_n[n]:
                media_n.append(teste.tempo_medio())
            for teste in teste_n[n]:
                if teste.tempo_desvio() == 0:
                    stdev_n.append(np.std(media_n))
                else:
                    stdev_n.append(teste.tempo_desvio())
            media.append(np.mean(media_n))
            stdev.append(np.mean(stdev_n))

        # Retornar dataframe
        return pd.DataFrame({'n': valores_n, 'media': media, 'desvio': stdev})

    def dados_rota_solucao(self):
        rotas = []
        fatores = []
        if self.__testes_executados is None:
            return None
        qaps = list(range(len(self.__testes_executados)))
        for teste in self.__testes_executados:
            rotas += teste.rota_resolvido()
            fatores += teste.fator_resolvido()
        return pd.DataFrame({'qap': qaps, 'rota': rotas, 'fator': fatores})

    def grafico_tempo_execucao(self):
        """
        Gera gráfico com dados relacionados ao tempo de execução dos testes

        :return: Gráfico pyplot dos dados de tempo de execução
        """

        # Garante que foi executado
        if self.__testes_executados is None:
            return None

        df = self.dados_tempo_execucao()
        ax = plt.subplot()
        ax.plot(df['n'], df['media'], 'b', label="media")
        ax.errorbar(df['n'], df['media'], df['desvio'], linestyle='None', ecolor='r', label="desvio padrão")
        ax.legend(loc='upper left')
        ax.set_xlabel("Número de dependências")
        ax.set_ylabel("Segundos")
        ax.title.set_text("Tempo de execução: "+self.__alg.__name__)
        return ax

    # Métodos privados ########################################

    def __copy__(self):
        obj = QAPBancoSuite()
        obj.__alg = self.__alg
        obj.__testes = self.__testes
        obj.__testes_executados = self.__testes_executados
        return obj

    def __str__(self):
        string = f"QAPBancoSuite com {len(self.__testes)} testes\n"
        if self.__testes_executados is None:
            string += "<Não executado>"
        else:
            for teste in self.__testes_executados:
                string += str(teste) + '\n'
        return string
