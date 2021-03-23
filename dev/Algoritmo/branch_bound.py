# -*- coding: utf-8 -*-

# Imports
from scipy.optimize import linear_sum_assignment
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
                    C_bb[i][k][j][p] = int(D[i][j] * F[i][j][k][p] * 1000000)

    X, _ = passo_1(n, C_bb)
    return X


def passo_1(n, C_bb):
    # (1) Coletando elementos complementares
    C_bb = junta_elementos_complementares(n, C_bb)

    # (1) Resolve cada submatriz (LAP)
    for i in range(n):
        for k in range(n):
            C_bb = resolve_lap_submatriz(n, C_bb, i, k)

    return passo_2(n, C_bb, 0)


def passo_2(n, C_bb, R_linha):
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
    _, num_linhas = hungarian_linhas(n, C_leader)
    solucao_encontrada = num_linhas >= n
    X = np.zeros((n, n))
    js, ps = linear_sum_assignment(C_leader)
    for x in range(n):
        if not solucao_encontrada: break
        for y in range(n):
            if C_bb[js[x]][ps[x]][js[y]][ps[y]] != 0:
                solucao_encontrada = False
                break
    if solucao_encontrada:
        for x in range(n):
            X[js[x]][ps[x]] = 1
        return X, R_linha

    # (2) Segundo caso: aumento do R'
    if reducao > 0:
        return passo_3(n, C_bb, C_leader, R_linha)

    # (2) Terceiro caso: Sem solução. R' é uma borda inferior
    else:
        return None, R_linha


def passo_3(n, C_bb, C_leader, R_linha):
    # (3) Se todos os lideres forem zero
    if C_leader.sum() == 0:
        return None, R_linha

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

    return passo_4(n, C_bb, C_leader, R_linha)


def passo_4(n, C_bb, C_leader, R_linha):
    # (4) Roda novamente o algoritmo nas submatrizes cujos lideres foram zero no passo 2
    for i in range(n):
        for k in range(n):
            if C_leader[i][k] == 0:
                C_bb = resolve_lap_submatriz(n, C_bb, i, k)
    for i in range(n):
        for k in range(n):
            if C_leader[i][k] != 0:
                C_bb = resolve_lap_submatriz(n, C_bb, i, k)
    return passo_2(n, C_bb, R_linha)


def junta_elementos_complementares(n, C_bb):
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
    js, ps = linear_sum_assignment(C)
    menor_custo = 0
    for x in range(n):
        menor_custo += C[js[x]][ps[x]]

    # Retorna a matriz final e valor da solução
    return C_ha, menor_custo


def hungarian_linhas(n, C_ha):
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
