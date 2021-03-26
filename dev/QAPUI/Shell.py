# -*- coding: utf-8 -*-

# Imports
import matplotlib.pyplot as plt
import QAPBanco.utilidades as util
import pandas as pd
from QAPBanco.QAPBanco import QAPBanco
from QAPBancoAnalise.QAPBancoTeste import QAPBancoTeste
from QAPBancoAnalise.QAPBancoSuite import QAPBancoSuite
from Algoritmo.forca_bruta import forca_bruta
from Algoritmo.branch_bound import branch_bound
from Algoritmo.simulated_annealing import simulated_annealing
import warnings
from copy import copy


class Shell:
    """
    Inteface de Usuário textual
    """

    def __init__(self):

        # Valores padrão
        self.__qap = None
        self.__teste = None
        self.__suite = None
        self.__alg = None
        self.__repeticoes = 0
        self.__num_dependencias_min = 2
        self.__num_dependencias_max = 2
        self.__nao_compara = [branch_bound]

        # Opcoes
        self.__op_janelas = {
            0: ('Sair', None),
            1: ('Resolver uma QAP do banco', self.__mostrar_resolver_qap),
            2: ('Analisar algoritmo', self.__mostrar_analisar_algoritmo),
            3: ('Comparar algoritmos', self.__mostrar_comparar_algoritmos)
        }
        self.__op_carregar = {
            0: ('Sair', None),
            1: ('QAP nova (aleatória)', self.__mostrar_obter_dados_aleatorios),
            2: ('QAP salva', self.__mostrar_obter_dados_salvos),
            3: ('QAP real parcial', self.__mostrar_obter_dados_reais_parcial),
            4: ('QAP real completa', self.__mostrar_obter_dados_reais_completo)
        }
        self.__op_algoritmos = {
            0: ('Sair', None),
            1: ('Força Bruta', forca_bruta),
            2: ('Dual-Procedure Branch and Bound', branch_bound),
            3: ('Classic Simulated Annealing', simulated_annealing)
        }
        self.__op_salvar = {
            0: ('Nao salvar', None),
            1: ('Salvar', self.__mostrar_salvar_qap)
        }

    def iniciar_ui(self):
        """
        Inicializa a comunicação via terminal
        """
        warnings.simplefilter("ignore", UserWarning)
        self.__mostrar_boas_vindas()
        while True:
            opcao = self.__mostrar_menu_principal()
            if opcao is None:
                break
            else:
                opcao()
        self.__mostrar_despedida()

    ## Telas principais #######################################

    def __mostrar_boas_vindas(self):
        print("")
        print("====================================================")
        print("                    QAPBanco                        ")
        print("====================================================")
        print(" A APLICAÇÃO E ANÁLISE DE ALGORITMOS PARA O PROBLEMA")
        print("     DE LOGÍSTICA, ATENDENDO REQUISITOS DE RISCO")
        print("    OPERACIONAL, NUM BANCO PÚBLICO BRASILEIRO COM")
        print("            O USO DE ATRIBUIÇÃO QUADRÁTICA")
        print("====================================================")
        print(" PPCA-UnB 2/2020")
        print(" Algoritmos e Estruturas de Dados")
        print(" -> Prof. Edison Ishikawa")
        print("====================================================")
        print(" Grupo 10:")
        print(" -> José Carlos Ferrer Simões")
        print(" -> Tiago Pereira Vidigal")
        print(" -> William Oliveira Camelo")
        print("====================================================")

    def __mostrar_menu_principal(self):
        print("")
        print("-- Menu --------------------------------------------")
        print("")
        print("Escolha o que deseja fazer:")
        return self.__mostrar_selecao_opcao(self.__op_janelas)

    def __mostrar_despedida(self):
        print("")
        print("====================================================")
        print(" Até a próxima! :)")
        print("====================================================")
        print("")

    ## Carregar QAP ###########################################

    def __mostrar_escolher_qap(self):
        print("")
        print("Qual QAP deseja usar?")
        carga_qap = self.__mostrar_selecao_opcao(self.__op_carregar)
        if carga_qap is not None: carga_qap()
        print("")
        print(self.__qap)
        return carga_qap

    def __mostrar_obter_dados_aleatorios(self):
        print("")
        print("Quantas dependencias terá o problema?")
        while True:
            try:
                n = int(input())
                break
            except:
                print("Entrada inválida! Digite um inteiro.")
        if n < 2:
            print("Forçando 'n' para valor mínimo 2")
            n = 2
        self.__qap = QAPBanco(util.gerar_entrada_aleatoria(n))

    def __mostrar_obter_dados_salvos(self):
        print("")
        print("Qual o nome do arquivo (sem extensão)?")
        self.__qap = QAPBanco(util.recuperar_dados(nome=input()))

    def __mostrar_obter_dados_reais_parcial(self):
        print("")
        print("Quantas dependências quer pegar?")
        while True:
            try:
                n = int(input())
                break
            except:
                print("Entrada inválida! Digite um inteiro.")
        if n < 2:
            print("Forçando 'n' para valor mínimo 2")
            n = 2
        print("")
        print(f"Pegando {n} dependencias aleatórias dos dados reais...")
        self.__qap = QAPBanco(util.gerar_entrada(max_dependencias=n))

    def __mostrar_obter_dados_reais_completo(self):
        self.__qap = QAPBanco(util.gerar_entrada())

    ## Resolver QAP ###########################################

    def __mostrar_resolver_qap(self):
        print("")
        print("-- Resolver QAP ------------------------------------")
        print("")
        if self.__mostrar_escolher_qap() is None: return
        if self.__mostrar_escolher_algoritmo() is None: return
        self.__mostrar_teste()
        self.__mostrar_salvar()

    def __mostrar_teste(self):
        print("")
        print("Rodando teste...")
        self.__teste = QAPBancoTeste(self.__qap)
        self.__teste.resolver_problema_com(self.__alg)
        print(self.__teste)

    def __mostrar_salvar(self):
        print("")
        print("Deseja salvar a QAP usada?")
        salvar_qap = self.__mostrar_selecao_opcao(self.__op_salvar)
        if salvar_qap is not None: salvar_qap()
        return salvar_qap

    def __mostrar_salvar_qap(self):
        print("")
        print("Qual o nome do arquivo (sem extensão)?")
        util.salvar_dados(self.__qap.resgatar_dependencias(), nome=input())

    ## Analises ###############################################

    def __mostrar_analisar_algoritmo(self):
        print("")
        print("-- Analisar algoritmo ------------------------------")
        self.__alg = self.__mostrar_escolher_algoritmo()
        if self.__alg is not None:
            self.__mostrar_obter_config_teste()
            self.__gerar_problemas_aleatorios()
            self.__roda_suite_testes()
            self.__mostrar_analise()

    def __mostrar_analise(self):
        print("")
        print(self.__suite)
        print("Salvando imagem da analise...")
        plot = self.__suite.grafico_tempo_execucao()
        plt.savefig("../../resultados/analise_" + self.__alg.__name__ + ".png")
        plt.close()

    ## Comparar ###############################################

    def __mostrar_comparar_algoritmos(self):
        print("")
        print("-- Comparar algoritmos -----------------------------")
        self.__mostrar_obter_config_teste()
        self.__gerar_problemas_aleatorios()
        df_media = pd.DataFrame({'n': range(self.__num_dependencias_min, self.__num_dependencias_max + 1)})
        df_desvio = pd.DataFrame({'n': range(self.__num_dependencias_min, self.__num_dependencias_max + 1)})
        df_rota = pd.DataFrame({'qap': range(self.__repeticoes * (self.__num_dependencias_max - self.__num_dependencias_min + 1))})
        df_fator = pd.DataFrame({'qap': range(self.__repeticoes * (self.__num_dependencias_max - self.__num_dependencias_min + 1))})
        for alg in self.__op_algoritmos:
            self.__alg = self.__op_algoritmos[alg][1]
            if self.__alg in self.__nao_compara:
                print("")
                print(f"Não comparando '{self.__alg.__name__}'")
                continue
            if self.__alg is not None:
                print("")
                print(f"Usando '{self.__alg.__name__}'", end="")
                self.__roda_suite_testes()
                df_rota = df_rota.merge(self.__suite.dados_rota_solucao()[['qap', 'rota']], on='qap')
                df_rota.rename(columns={'rota':self.__alg.__name__}, inplace=True)
                df_fator = df_fator.merge(self.__suite.dados_rota_solucao()[['qap', 'fator']], on='qap')
                df_fator.rename(columns={'fator':self.__alg.__name__}, inplace=True)
                df_media = df_media.merge(self.__suite.dados_tempo_execucao()[['n', 'media']], on='n')
                df_media.rename(columns={'media':self.__alg.__name__}, inplace=True)
                df_desvio = df_desvio.merge(self.__suite.dados_tempo_execucao()[['n', 'desvio']], on='n')
                df_desvio.rename(columns={'desvio':self.__alg.__name__}, inplace=True)
                plot = self.__suite.grafico_tempo_execucao()
                plt.savefig("../../resultados/analise_" + self.__alg.__name__ + ".png")
                plt.close()
        print("")
        print("Rotas")
        print(df_rota)
        print("")
        print("Fatores")
        print(df_fator)
        print("")
        print("Médias")
        print(df_media)
        print("")
        print("Desvios padrão")
        print(df_desvio)
        print("")
        print("Salvando imagem da comparação...")
        ax = df_media.plot(x='n', yerr=df_desvio)
        ax.legend(loc='upper left')
        ax.set_xlabel("Número de dependências")
        ax.set_ylabel("Tempo de execução (s)")
        ax.locator_params(axis='x', integer=True)
        ax.title.set_text("Comparação dos algoritmos")
        ax.figure.savefig("../../resultados/comparacao_algoritmos.png")
        print("Salvando resultados...")
        util.salvar_dados(df_rota, "../../resultados", "comparacao_rota")
        util.salvar_dados(df_fator, "../../resultados", "comparacao_fator")
        util.salvar_dados(df_media, "../../resultados", "comparacao_media")
        util.salvar_dados(df_desvio, "../../resultados", "comparacao_desvio")


    ## Outros #################################################

    def __mostrar_escolher_algoritmo(self):
        print("")
        print("Qual algoritmo deseja usar?")
        self.__alg = self.__mostrar_selecao_opcao(self.__op_algoritmos)
        return self.__alg

    def __mostrar_selecao_opcao(self, opcoes):
        for opcao in opcoes.keys():
            print(f"{opcao}) {opcoes[opcao][0]}")
        print("")
        while True:
            try:
                print("Opção: ", end="")
                sel = int(input())
                if sel not in opcoes.keys():
                    print("Opção inválida!")
                else:
                    break
            except:
                print("Opção inválida!")
        return opcoes[sel][1]

    def __gerar_problemas_aleatorios(self):
        print("")
        print(f"Gerando {self.__repeticoes} problema(s) aleatório(s) de n={self.__num_dependencias_min} até {self.__num_dependencias_max}...")
        test_n = list(range(self.__num_dependencias_min, self.__num_dependencias_max + 1))
        self.__qap = [QAPBanco(util.gerar_entrada_aleatoria(n)) for n in test_n for i in range(self.__repeticoes)]

    def __roda_suite_testes(self):
        print("")
        print("Rodando suite de testes...")
        self.__teste = [QAPBancoTeste(qap) for qap in self.__qap]
        self.__suite = QAPBancoSuite(self.__teste, self.__alg)
        self.__suite.rodar_testes()

    def __mostrar_obter_config_teste(self):
        print("")
        print("Qual o número máximo de dependências que quer analisar?")
        while True:
            try:
                self.__num_dependencias_max = int(input())
                break
            except:
                print("Entrada inválida! Digite um inteiro.")
        print("")
        print("Quantas repetições por número de dependências?")
        while True:
            try:
                self.__repeticoes = int(input())
                break
            except:
                print("Entrada inválida! Digite um inteiro.")

