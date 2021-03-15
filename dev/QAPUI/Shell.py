# -*- coding: utf-8 -*-

# Imports
import matplotlib.pyplot as plt
import QAPBanco.utilidades as util
from QAPBanco.QAPBanco import QAPBanco
from QAPBancoAnalise.QAPBancoTeste import QAPBancoTeste
from QAPBancoAnalise.QAPBancoSuite import QAPBancoSuite
from Algoritmo.forca_bruta import forca_bruta

class Shell:

    def __init__(self):

        # Valores padrão
        self.__qap = None
        self.__teste = None
        self.__suite = None
        self.__alg = None

        # Opcoes
        self.op_janelas = {
            0: ('Sair', None),
            1: ('Resolver uma QAP do banco', self.mostrar_resolver_qap),
            2: ('Analisar forca bruta', self.mostrar_analisar_forca_bruta)
        }
        self.op_carregar = {
            0: ('Sair', None),
            1: ('QAP nova (aleatória)', self.mostrar_obter_dados_aleatorios),
            2: ('QAP salva', self.mostrar_obter_dados_salvos)
        }
        self.op_algoritmos = {
            0: ('Sair', None),
            1: ('Força Bruta', forca_bruta)
        }
        self.op_salvar = {
            0: ('Nao salvar', None),
            1: ('Salvar', util.salvar_dados)
        }

    def iniciar_ui(self):
        self.mostrar_boas_vindas()
        while True:
            opcao = self.mostrar_menu_principal()
            if opcao is None:
                break
            else:
                opcao()
        self.mostrar_despedida()

    ## Telas principais #######################################

    def mostrar_boas_vindas(self):
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

    def mostrar_menu_principal(self):
        print("")
        print("-- Menu --------------------------------------------")
        print("")
        print("Escolha o que deseja fazer:")
        return self.mostrar_selecao_opcao(self.op_janelas)

    def mostrar_despedida(self):
        print("")
        print("====================================================")
        print(" Até a próxima! :)")
        print("====================================================")
        print("")

    ## Resolver QAP ###########################################

    def mostrar_resolver_qap(self):
        print("")
        print("-- Resolver QAP ------------------------------------")
        print("")
        if self.mostrar_escolher_qap() is None: return
        if self.mostrar_escolher_algoritmo() is None:  return
        self.mostrar_teste()
        self.mostrar_salvar()

    def mostrar_teste(self):
        print("")
        print("Rodando teste...")
        self.__teste = QAPBancoTeste(self.__qap)
        self.__teste.resolver_problema_com(self.__alg)
        print(self.__teste)
        print("Solucao:     ", self.__qap.rota_solucao())

    def mostrar_salvar(self):
        print("")
        print("Deseja salvar a QAP usada?")
        salvar_qap = self.mostrar_selecao_opcao(self.op_salvar)
        if salvar_qap is not None: salvar_qap(self.__qap.resgatar_dependencias())
        return salvar_qap

    ## Carregar QAP ###########################################

    def mostrar_escolher_qap(self):
        print("")
        print("Qual QAP deseja usar?")
        carga_qap = self.mostrar_selecao_opcao(self.op_carregar)
        if carga_qap is not None: carga_qap()
        return carga_qap

    def mostrar_obter_dados_aleatorios(self):
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
        print(self.__qap)

    def mostrar_obter_dados_salvos(self):
        print("")
        print("Recuperando ultimo dado salvo...")
        self.__qap = QAPBanco(util.recuperar_dados())
        print(self.__qap)

    ## Analises ###############################################

    def mostrar_analisar_forca_bruta(self):
        print("")
        print("-- Analisar: Forca Bruta ---------------------------")
        print("")
        self.__alg = forca_bruta
        self.mostrar_analise()

    def mostrar_analise(self):
        print("Qual o número máximo de dependências que quer analisar?")
        while True:
            try:
                max_n = int(input())
                break
            except:
                print("Entrada inválida! Digite um inteiro.")
        print("")
        print("Quantas repetições por número de dependências?")
        while True:
            try:
                repeticoes = int(input())
                break
            except:
                print("Entrada inválida! Digite um inteiro.")
        print("")
        print("Preparando suite de testes...")
        test_n = list(range(2, max_n + 1))
        self.__qap = [QAPBanco(util.gerar_entrada_aleatoria(n)) for n in test_n]
        self.__teste = [QAPBancoTeste(qap) for qap in self.__qap]
        self.__suite = QAPBancoSuite(self.__teste, self.__alg)
        print("Rodando suite de testes...")
        self.__suite.rodar_testes()
        print("")
        print(self.__suite)
        print("Salvando imagem da analise...")
        plot = self.__suite.grafico_tempo_execucao()
        plt.savefig("../../dados/analise_" + self.__alg.__name__ + ".png")
        plt.close()


    ## Outros #################################################

    def mostrar_escolher_algoritmo(self):
        print("")
        print("Qual algoritmo deseja usar?")
        self.__alg = self.mostrar_selecao_opcao(self.op_algoritmos)
        return self.__alg

    def mostrar_selecao_opcao(self, opcoes):
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


shell = Shell()
shell.iniciar_ui()
