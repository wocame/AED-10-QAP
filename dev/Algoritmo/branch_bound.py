# -*- coding: utf-8 -*-

# Imports
from itertools import permutations

import numpy as np
from QAPBanco.QAPBanco import QAPBanco


# Algoritmo
def branch_bound(n, D, F):
    """
    Algoritmo Branch-and-Bound para calcular QAP do banco
    Originalmente descrevemos a matriz de custo de QAP como C[i][j][k][p], sendo:
       '-> i = dependencia de origem
       '-> j = dependencia de destino
       '-> k = posição da rota de origem
       '-> p = posição da rota de destino
    Para utilizar o branch and bound, consideramos C uma matrix N² (origem) por N² (destino)
    Dessa forma, os indices de origem i e k se assemelham aos da matriz de permutação X (dependencia por posição)
       '-> C_bb[i][k][j][p] = C[i][j][k][p]
    Podemos fixar uma escolha de dependencia e posição na rota, criamos um branch com problema com N-1 dependencias
       '-> Fazendo C_bb[i][k] = 1, os demais C_bb[i][*] e C_bb[*][k] são forçados a 0
       '-> C do branch = C_branch = C_bb[ic][kc] para ic,kc de 0 a N-1, ic != i, kc != k
    Não só isso, combinações que consideram uma dependencia ou posição de destino diferentes de i e j são impossíveis.
    Isso quer dizer que, dada a origem i e k já fixada:
       '-> Destino j=i com p!=k é impossível
       '-> Destino j!=i com p=k é impossível
       '-> C_branch[ic][kc] = C_bb[ic][kc][jc][pc] para jc,pc de 0 a N-1, jc != i, pc != k
    Com a redução de C para uma matriz (N-1)² por (N-1)², temos um novo problema de QAP reduzido (nosso branch)
    Porém, note que temos que incluir o gasto da origem i em k até os destinos j em p que estão no branch.
    Não só isso, temos que considerar os custos das combinações com destino i em k que foram removidos na formula acima.
    Por causa disso, somamos em todos os elementos de cada C_branch os respectivos custos listados acima.
    Isso garante que os branchs consideram o custo ja selecionado pela dependencia i fixada na posiçao k
       '-> C_branch_final = C_branch[ic][kc][jc][kc] + C_bb[i][k][jc][kc] + C_bb[ic][kc][i][k]
    Com isso, podemos calcular informações de custo de cada branch: o custo real e estimativas de borda
    Essas estimativas de borda são úteis para cancelar o calculo de branches não promissores (fathoming)
    Dessa forma, cada novo branch tem suas bordas inferiores e superiores calculadas antes de calcular seu custo real.
    Se o menor valor estimado for maior que o maior valor estimado para o melhor caso encontrado até então, abortamos
    Caso contrário, continuamos e, caso o branch se mostre melhor, atualizamos a borda superior considerada
    
    :param n: Número de dependências
    :param D: Matriz de custo de deslocamento entre dependências
    :param F: Matriz de fator de risco
    :return: Matriz de escolha com rota ótima
    """

    # Matrix C N^4 para C_bb N² por N²
    # '-> i = dependencia de origem
    # '-> j = dependencia de destino
    # '-> k = posição da rota de origem
    # '-> p = posição da rota de destino
    # '-> C_bb[i][k][j][p] = C[i][j][k][p]
    C_bb = np.zeros((n, n, n, n))
    for i in range(n):
        for j in range(n):
            for k in range(n):
                for p in range(n):
                    C_bb[i][k][j][p] = D[i][j] * F[i][j][k][p]

    print("")
    print(f"Initial:\n{C_bb}:")
    X, custo = branch(n, C_bb, None, None)
    print("")
    print(f"Solucao com custo {custo}:")
    print(X)
    return X

def branch(n, C_bb, custo_menor, ub_menor):

    # Caso especial: final da árvore
    if n == 1:
        return [1], C_bb[0][0][0][0]

    # BRANCH: Fixa uma dependência em uma posição e gera um problema N-1
    # '-> Fazendo C_bb[i][k] = 1, os demais C_bb[i][*] e C_bb[*][k] são forçados a 0
    X = None
    for i in range(n):
        for k in range(n):

            # Formulando custo do problema N-1
            # '-> C do branch = C_branch = C_bb[ic][kc] para ic,kc de 0 a N-1, ic != i, kc != k
            # '-> C_branch[ic][kc] = C[ic][kc][jc][pc] para jc,pc de 0 a N-1, jc != i, pc != k
            # '-> C_branch_final = C_branch[ic][kc][jc][kc] + C_bb[i][k][jc][kc] + C_bb[ic][kc][i][k]
            i_branch = [ic for ic in range(n) if ic != i]
            k_branch = [kc for kc in range(n) if kc != k]
            j_branch = [jc for jc in range(n) if jc != i]
            p_branch = [pc for pc in range(n) if pc != k]
            C_branch = [[[[C_bb[ic][kc][jc][pc] + C_bb[ic][kc][i][k] + C_bb[i][k][jc][pc]
                           for pc in p_branch]
                          for jc in j_branch]
                         for kc in k_branch]
                        for ic in i_branch]
            print(f"Branch n={n}, indice {i} {k}")

            # BOUND: Checando bounds do problema
            lb, ub = bound_HGB(n - 1, C_branch)
            if n == 4:
                print(f"Lower bound={lb}, Upper bound {ub}")
            if ub_menor is not None:
                if lb > ub_menor:
                    print(f"But lower bound {lb} is greater or equal {ub_menor}")
                    continue
                if ub < ub_menor:
                    ub_menor = ub
                    print(f"Has promissing lower bound {lb} less then {ub_menor}")

            # Branching recursivo
            X_branch, custo_branch = branch(n-1, C_branch, custo_menor, ub_menor)

            # Confere se uma solução melhor foi encontrada
            if X_branch is None:
                continue
            if custo_menor is not None:
                if custo_branch > custo_menor:
                    print(f"Mas custo {custo_branch} maior que {custo_menor}")
                    continue

            # Atualiza solucao com menor custo
            custo_menor = custo_branch
            X = np.zeros((n, n))
            X[i][k] = 1
            X_aux = [x for x in np.nditer(X_branch)]
            for ic in i_branch:
                for kc in k_branch:
                    X[ic][kc] = X_aux.pop(0)
            print(f"Novo menor com custo {custo_branch}!")
            print(X)

    return X, custo_menor

def bound_HGB(n, C_branch):

    # Gera todas as possiveis permutações x
    permutacao = [np.array(perm) for perm in permutations(np.identity(n-1))]

    # (1) Calcula problemas de assinalamento lineares (LAP) de cada submatriz
    # Adiciona o valor encontrado ao lider da submatrix
    L_lb = np.zeros((n, n))
    L_ub = np.zeros((n, n))
    for i in range(n):
        for k in range(n):
            custos = []
            for X in permutacao:
                custo = 0
                for j in range(n):
                    if k != i:
                        for p in range(n):
                            if p != j:
                                custo += C_branch[i][k][j][p]
                custos += [custo]
            L_lb[i][k] = C_branch[i][k][i][k] + min(custos)
            L_ub[i][k] = C_branch[i][k][i][k] + max(custos)

    # (2) Soma dos custos dos lideres revisados
    lb_candidatos = []
    ub_candidatos = []
    for X in permutacao:
        lb_candidato = 0
        ub_candidato = 0
        for i in range(n):
            for k in range(n):
                lb_candidato += L_lb[i][k]
                ub_candidato += L_ub[i][k]
        lb_candidatos += [lb_candidato]
        ub_candidatos += [ub_candidato]

    # Retorna lower e upper bounds
    return min(lb_candidatos), max(ub_candidatos)
