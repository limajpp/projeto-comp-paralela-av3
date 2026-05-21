import random

def gerar_matriz(tamanho):
    """Gera matriz com valores aleatórios."""
    return [[random.random() for _ in range(tamanho)] for _ in range(tamanho)]

def multiplicar_submatriz(sub_A, B):
    """Realiza a multiplicação da submatriz de A com a matriz B."""
    tamanho_colunas_B = len(B[0])
    resultado = []
    for linha_A in sub_A:
        linha_resultado = [0.0] * tamanho_colunas_B
        for j in range(tamanho_colunas_B):
            for k in range(len(linha_A)):
                linha_resultado[j] += linha_A[k] * B[k][j]
        resultado.append(linha_resultado)
    return resultado

def multiplicacao_serial(A, B, tamanho):
    """Multiplicação clássica (1 núcleo) para servir de baseline."""
    C = [[0.0 for _ in range(tamanho)] for _ in range(tamanho)]
    for i in range(tamanho):
        for j in range(tamanho):
            for k in range(tamanho):
                C[i][j] += A[i][k] * B[k][j]
    return C

