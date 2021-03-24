# -*- coding: utf-8 -*-

# Imports
from scipy.optimize import linear_sum_assignment
from itertools import permutations
from copy import copy

import numpy as np


# Algoritmo
def branch_bound(n, D, F):
    """
    Implementação do Dual-Procedure Branch and Bound

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
    # Uma vez que esse método considera apenas números inteiros, o custo é multiplicado
    # por um fator de forma a permitir que casas decimais suficientes sejam consideradas.
    C_bb = np.zeros((n, n, n, n))
    for i in range(n):
        for j in range(n):
            for k in range(n):
                for p in range(n):
                    C_bb[i][k][j][p] = int(D[i][j] * F[i][j][k][p] * 1000)

    C_linha, menor_custo = hgb(n, C_bb)
    X, _ = branch(n, C_linha, menor_custo)
    return X

def branch(n, C_bb, menor_custo):
    """
    Função de ramificação do Dual-Procedure Branch and Bound

    :param n: Número de dependências
    :param C_bb: Matriz de custo N² por N²
    :param menor_custo: Menor custo encontrado até o momento
    :return: Matriz de escolha com rota ótima e seu custo
    """

    # Caso especial: final da árvore
    if n == 1:
        return [1], C_bb[0][0][0][0]

    # BRANCH: Fixa uma dependência em uma posição e gera um problema N-1
    # '-> Fazendo C_bb[i][k] = 1, os demais C_bb[i][*] e C_bb[*][k] são forçados a 0
    X = None
    for i in range(n):
        for k in range(n):

            # Formulando custo do problema N-1 fixando C[i][k][i][k]
            # '-> C do branch = C_branch = C_bb[ic][kc] para ic,kc de 0 a N-1, ic != i, kc != k
            # '-> C_branch[ic][kc] = C[ic][kc][jc][pc] para jc,pc de 0 a N-1, jc != i, pc != k
            # '-> C_branch_final = C_branch[ic][kc][jc][kc] + C_bb[i][k][jc][kc] + C_bb[ic][kc][i][k]
            i_branch = [ic for ic in range(n) if ic != i]
            k_branch = [kc for kc in range(n) if kc != k]
            j_branch = [jc for jc in range(n) if jc != i]
            p_branch = [pc for pc in range(n) if pc != k]
            C_branch = [[[[C_bb[ic][kc][jc][pc] + C_bb[i][k][ic][kc]
                           for pc in p_branch]
                          for jc in j_branch]
                         for kc in k_branch]
                        for ic in i_branch]

            # BOUND: Checando bounds do problema
            C_branch, lb = hgb(n - 1, C_branch)

            if menor_custo is not None:
                if lb > menor_custo:
                    continue
            menor_custo = C_bb[i][k][i][k] + lb
            for ic in i_branch:
                for kc in k_branch:
                    menor_custo += C_bb[i][k][i][k]

            # Branching recursivo
            X_branch, custo_branch = branch(n-1, C_branch, menor_custo)
            if X_branch is None:
                continue

            # Atualiza solucao com menor custo
            X = np.zeros((n, n))
            X[i][k] = 1
            X_aux = [x.item() for x in np.nditer(X_branch)]
            for ic in i_branch:
                for kc in k_branch:
                    X[ic][kc] = X_aux.pop(0)

    return X, menor_custo

def hgb(n, C_bb):
    """
    Primeiro passo do algoritmo de Hahn-Grant Bound para calculo do limite inferior
    Junta os elementos complementares da matriz e resolve a LAP das submatrizes.

    :param n: Número de dependências
    :param C_bb: Matriz de custo N² por N²
    :return: Matriz de custo C' no término do algoritmo :method:hungarian e o limite inferior
    """

    if n == 1:
        return C_bb, C_bb[0][0][0][0]

    # (1) Coletando elementos complementares
    C_bb = junta_elementos_complementares(n, C_bb)

    # (1) Resolve cada submatriz (LAP)
    for i in range(n):
        for k in range(n):
            C_bb = resolve_lap_submatriz(n, C_bb, i, k)

    return hgb_passo_2(n, C_bb, 0)


def hgb_passo_2(n, C_bb, R_linha):
    """
    Segundo passo do algoritmo de Hahn-Grant Bound para calculo do limite inferior.
    Roda o algoritmo húngaro na matriz de líderes e define o que deve ser feito:
    * (1) Confere se a solução foi encontrada, returnando ela caso positivo
    * (2) Se solução não encontrada, confere se teve um aumento de R' e roda o passo 3
    * (3) Se a solução não foi encontrada e não teve aumento de R', retorna o limite inferior encontrado

    :param n: Número de dependências
    :param C_bb: Matriz de custo N² por N²
    :param R_linha: Fator de redução R' (limite inferior) encontrado até o momento
    :return: Matriz de custo reduzida e o limite inferior
    """
    while True:
        C_leader = np.zeros((n, n))
        for i in range(n):
            for k in range(n):
                C_leader[i][k] = C_bb[i][k][i][k]

        # (2) Hungarian Algorithm na matriz de lideres
        C_leader, reducao = hungarian(n, C_leader)
        R_linha += reducao
        for i in range(n):
            for k in range(n):
                C_bb[i][k][i][k] = C_leader[i][k]

        # (2) Primeiro caso: solução foi encontrada
        C_test = np.zeros((n, n))
        _, num_linhas = hungarian_linhas(n, C_leader)
        if num_linhas >= n:
            for i in range(n):
                for k in range(n):
                    if C_leader[i][k] == 0:
                        C_test[i][k] = 1

            # Testa as possiveis solucoes
            ic = []
            kc = []
            while True:
                size = len(ic) + len(kc)
                for i in [i for i in range(n) if i not in ic]:
                    if sum(C_test[i]) == 1:
                        for k in [k for k in range(n) if k not in kc]:
                            ic += [i]
                            kc += [k]
                for k in [k for k in range(n) if k not in kc]:
                    if sum(C_test[:][k]) == 1:
                        for i in [i for i in range(n) if i not in ic]:
                            ic += [i]
                            kc += [k]
                if size == len(ic) + len(kc):
                    break

            # Gera matrizes de permutação de possiveis soluções
            permutacao = [np.array(perm) for perm in permutations(np.identity(n))]
            for x in range(len(ic)):
                permutacao = [perm for perm in permutacao if perm[ic[x]][kc[x]] == 1]
            for X in permutacao:
                solucao_confirmada = True
                jc, pc = linear_sum_assignment(X, True)
                for x in range(n):
                    for y in range(n):
                        if C_bb[jc[x]][pc[x]][jc[y]][pc[y]] != 0:
                            solucao_confirmada = False
                            break
                    if not solucao_confirmada: break

                # Solução realmente confirmada!
                if solucao_confirmada:
                    return C_bb, R_linha

        # (2) Segundo caso: aumento do R'
        # Executa proximos passos antes de tentar novamente
        if reducao > 0:
            C_bb, R_linha = hgb_passo_3(n, C_bb, C_leader, R_linha)

        # (2) Terceiro caso: Sem solução. R' é uma borda inferior
        else:
            return C_bb, R_linha


def hgb_passo_3(n, C_bb, C_leader, R_linha):
    """
    Terceiro passo do algoritmo de Hahn-Grant Bound para calculo do limite inferior.
    Se todos os líderes forem zero, retorna o limite inferior.
    Caso contrário, redistribui uniformimente o valor dos lideres em suas submatrizes respectivas

    :param n: Número de dependências
    :param C_bb: Matriz de custo N² por N²
    :param R_linha: Fator de redução R' (limite inferior) encontrado até o momento
    :return: Matriz de custo com valor dos lideres e o limite inferior e o limite inferior
    """

    # (3) Se todos os lideres forem zero
    if C_leader.sum() == 0:
        return C_bb, R_linha

    # (3) Caso contrário, para cada lider que não seja 0, distribuir uniformimente o valor em sua submatriz
    # Lembrando que os valores precisam ser inteiros
    for i in range(n):
        for k in range(n):
            if C_leader[i][k] != 0:
                base = int(C_leader[i][k]) // (n - 1)
                resto = int(C_leader[i][k]) % (n - 1) * (n - 1)
                incr_matriz = np.zeros((n, n))
                for j in [j for j in range(n) if j != i]:
                    for p in [p for p in range(n) if p != k]:
                        if resto == 0:
                            incr_matriz[j][p] = base
                        else:
                            incr_matriz[j][p] = base + 1
                            resto -= 1
                C_bb[i][k] = [list(map(sum, zip(*t))) for t in zip(C_bb[i][k], incr_matriz)]
                C_bb[i][k][i][k] -= C_leader[i][k]

    C_bb = junta_elementos_complementares(n, C_bb)

    return hgb_passo_4(n, C_bb, C_leader, R_linha)


def hgb_passo_4(n, C_bb, C_leader, R_linha):
    """
    Quarto passo do algoritmo de Hahn-Grant Bound para calculo do limite inferior.
    Resolve a LAP das submatrizes, primeiros das que tinham líder zero e depois as demais

    :param n: Número de dependências
    :param C_bb: Matriz de custo N² por N²
    :param C_leader: Matriz de custo dos líderes
    :param R_linha: Fator de redução R' (limite inferior) encontrado até o momento
    :return: Matriz de custo reduzida e o limite inferior
    """
    # (4) Roda novamente o algoritmo nas submatrizes cujos lideres foram zero no passo 2
    for i in range(n):
        for k in range(n):
            if C_leader[i][k] == 0:
                C_bb = resolve_lap_submatriz(n, C_bb, i, k)
    for i in range(n):
        for k in range(n):
            if C_leader[i][k] != 0:
                C_bb = resolve_lap_submatriz(n, C_bb, i, k)
    return C_bb, R_linha


def junta_elementos_complementares(n, C_bb):
    """
    Junta os elementos complementares na matriz de custo

    :param n: Número de dependências
    :param C_bb: Matriz de custo N² por N²
    :return: Matriz de custo com os elementos complementares somados e concentrados nos indices superiores
    """
    for i in range(n):
        for k in range(n):
            j_branch = [jc for jc in range(n) if jc != i]
            p_branch = [pc for pc in range(n) if pc != k]
            for j in j_branch:
                for p in p_branch:
                    if j < i:
                        C_bb[i][k][j][p] = 0
                    else:
                        C_bb[i][k][j][p] += C_bb[j][p][i][k]
    return C_bb


def resolve_lap_submatriz(n, C_bb, i, k):
    """
    Resolve o Linear Assignment Problem da submatriz C_bb[i][k]

    :param n: Número de dependências
    :param C_bb: Matriz de custo N² por N²
    :param i: Índice da dependência escolhida
    :param k: Índice da posição em que a dependência escolhida está
    :return: Matriz de custo reduzida presente no término do algoritmo :method:hungarian
    """
    j_branch = [jc for jc in range(n) if jc != i]
    p_branch = [pc for pc in range(n) if pc != k]
    C_branch = np.array([[C_bb[i][k][j][p] for p in p_branch] for j in j_branch])

    # (1) Move custo dos elementos complementares das submatrizes acima
    if i > 0:
        C_move = [[C_bb[j][p][i][k] for p in p_branch] for j in range(i)]
        for j in range(i):
            for p in range(n - 1):
                C_branch[j][p] = C_move[j][p]
            for p in p_branch:
                C_bb[j][p][i][k] = 0

    # Roda algoritmo hungaro
    C_branch, custo_branch = hungarian(n - 1, C_branch)

    # (1) Adicionando custo no lider da submatriz
    C_bb[i][k][i][k] += custo_branch
    C_aux = [c.item() for c in np.nditer(C_branch)]
    for j in j_branch:
        for p in p_branch:
            C_bb[i][k][j][p] = C_aux.pop(0)

    # (1) Destroca elementos complementares
    if i > 0:
        C_move = np.array([[C_branch[j][p] for p in range(n - 1)] for j in range(i)])
        C_move = [c.item() for c in np.nditer(C_move)]
        for j in range(i):
            for p in p_branch:
                C_bb[j][p][i][k] = C_move.pop(0)

    # Garante elementos complementares nas submatrizes em baixo estão zerados
    for i in range(n):
        for k in range(n):
            j_branch = [jc for jc in range(n) if jc != i]
            p_branch = [pc for pc in range(n) if pc != k]
            for j in j_branch:
                for p in p_branch:
                    if j < i:
                        C_bb[i][k][j][p] = 0
    return C_bb


def hungarian(n, C):
    """
    Hungarian Algorithm para resolver LAPs

    :param n: Número de dependências
    :param C: Matriz de custos
    :return: Matriz de custo reduzida e custo encontrado
    """
    C_ha = np.array(copy(C))

    # Para cada linha, subtrai todos os elementos pelo menos valor
    for j in range(n):
        menor_elemento = min(C_ha[j])
        for p in range(n):
            C_ha[j][p] -= menor_elemento

    # Para cada coluna, subtrai todos os elementos pelo menos valor
    for p in range(n):
        menor_elemento = min(C_ha[:, p])
        for j in range(n):
            C_ha[j][p] -= menor_elemento

    # Enquanto não tiver pelo menos n linhas com mais de 1 zero
    while True:

        linhas_zero, num_linhas = hungarian_linhas(n, C_ha)
        if num_linhas >= n:
            break

        # Caso contrário:
        else:

            # Identifica celula não marcadas com menor valor
            nao_marcados = []
            for j in range(n):
                for p in range(n):
                    if linhas_zero[j][p] == 0:
                        nao_marcados += [C_ha[j][p]]
            menor_nao_marcado = min(nao_marcados)

            # Subtrai menor valor não marcado nas linhas sem cruzamento
            for j in range(n):
                if sum(linhas_zero[j]) < n:
                    for p in range(n):
                        C_ha[j][p] -= menor_nao_marcado

            # Adiciona menor valor não marcado nas colunas com cruzamento
            for p in range(n):
                if sum(linhas_zero[:, p]) == n:
                    for j in range(n):
                        C_ha[j][p] += menor_nao_marcado

    # Calcula custo da solução encontrada
    js, ps = linear_sum_assignment(C_ha)
    menor_custo = 0
    for x in range(n):
        menor_custo += C[js[x]][ps[x]]

    # Retorna a matriz final e valor da solução
    return C_ha, menor_custo


def hungarian_linhas(n, C_ha):
    """
    Traça as linhas de zeros para resolução do algoritmo hungaro

    :param n: Número de dependências
    :param C_ha: Matriz de custos sendo editado pelo algoritmo hungaro
    :return: Matriz de linhas de zeros e número de linhas
    """
    # Assinala zeros
    assinala_zero = np.array([[None] * n for x in range(n)])
    for j in range(n):
        for p in range(n):
            if C_ha[j][p] == 0 and assinala_zero[j][p] is None:
                assinala_zero[j] = [0] * n
                assinala_zero[:, p] = [0] * n
                assinala_zero[j][p] = 1
                break

    # Marca linhas e colunas
    marca_linha = np.zeros(n)
    marca_coluna = np.zeros(n)
    nova_linha = np.zeros(n)
    nova_coluna = np.zeros(n)
    for j in range(n):
        if 1 not in assinala_zero[j]:
            marca_linha[j] = 1
            nova_linha[j] = 1
    while True:
        if sum(nova_linha) == 0:
            break
        else:
            for j in range(n):
                if nova_linha[j]:
                    for p in range(n):
                        if marca_coluna[p] == 0 and C_ha[j, p] == 0:
                            marca_coluna[p] = 1
                            nova_coluna[p] = 1
                    nova_linha[j] = 0
        if sum(nova_coluna) == 0:
            break
        else:
            for p in range(n):
                if nova_coluna[p]:
                    for j in range(n):
                        if marca_linha[j] == 0 and assinala_zero[j][p] == 1:
                            marca_linha[j] = 1
                            nova_linha[j] = 1
                    nova_coluna[p] = 0

    # Gera minimo conjunto de linhas
    linhas_zero = np.zeros((n, n))
    num_linhas = 0
    for j in range(n):
        if marca_linha[j] == 0:
            linhas_zero[j] = [1] * n
            num_linhas += 1
    for p in range(n):
        if marca_coluna[p]:
            linhas_zero[:, p] = [1] * n
            num_linhas += 1

    # Retorna linhas encontradas
    return linhas_zero, num_linhas


def test_vector():
    """
    Vetor de testes do artigo usado de base pro desenvolvimento do HGB

    '-> HAHN, P.; GRANT, T.; Lower Bounds For The Quadratic Assignment Problem Based Upon A Dual Formulation

    :return: Vetor de teste com 4 dependências
    """
    return [[[[105, 0, 0, 0],
              [0, 60, 120, 30],
              [0, 70, 140, 35],
              [0, 20, 40, 10]],

             [[0, 105, 0, 0],
              [108, 0, 54, 24],
              [126, 0, 63, 28],
              [36, 0, 18, 8]],

             [[0, 0, 105, 0],
              [30, 36, 0, 48],
              [35, 42, 0, 56],
              [10, 12, 0, 16]],

             [[0, 0, 0, 105],
              [48, 0, 90, 0],
              [56, 0, 105, 0],
              [16, 0, 30, 0]]],

            [[[0, 60, 120, 30],
              [90, 0, 0, 0, 0],
              [0, 50, 100, 25],
              [0, 60, 120, 30]],

             [[108, 0, 54, 24],
              [0, 90, 0, 0],
              [90, 0, 45, 20],
              [108, 0, 54, 24]],

             [[30, 36, 0, 48],
              [0, 0, 90, 0],
              [25, 30, 0, 40],
              [30, 36, 0, 48]],

             [[48, 0, 90, 0],
              [0, 0, 0, 90],
              [40, 0, 75, 0],
              [48, 0, 90, 0]]],

            [[[0, 70, 140, 35],
              [0, 50, 100, 25],
              [105, 0, 0, 0],
              [0, 10, 20, 5]],

             [[126, 0, 63, 28],
              [90, 0, 45, 20],
              [0, 105, 0, 0],
              [18, 0, 9, 4]],

             [[35, 42, 0, 56],
              [25, 30, 0, 40],
              [0, 0, 105, 0],
              [5, 6, 0, 8]],

             [[56, 0, 105, 0],
              [40, 0, 75, 0],
              [0, 0, 0, 105],
              [8, 0, 15, 0]]],

            [[[0, 20, 40, 10],
              [0, 60, 120, 30],
              [0, 10, 20, 5],
              [90, 0, 0, 0]],

             [[36, 0, 18, 8],
              [108, 0, 54, 24],
              [18, 0, 9, 4],
              [0, 90, 0, 0]],

             [[10, 12, 0, 16],
              [30, 36, 0, 48],
              [5, 6, 0, 8],
              [0, 0, 90, 0]],

             [[16, 0, 30, 0],
              [48, 0, 90, 0],
              [8, 0, 15, 0],
              [0, 0, 0, 90]]]]


# print(hgb_passo_1(4,test_vector()))
