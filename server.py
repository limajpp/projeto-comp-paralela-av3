import socket
import sys
from utils.rede import receber_dado, enviar_dado

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

def iniciar_servidor(porta):
    HOST = '127.0.0.1'
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, porta))
        s.listen(1)
        print(f"Servidor aguardando conexão na porta {porta}...")
        
        conn, addr = s.accept()
        with conn:
            print(f"Cliente conectado: {addr}")
            
            dados = receber_dado(conn)
            sub_A = dados['sub_A']
            B = dados['B']
            print(f"Dados recebidos. Multiplicando {len(sub_A)} linhas...")
            
            resultado = multiplicar_submatriz(sub_A, B)
            print("Cálculo concluído. Aguardando sinal de sincronismo do Cliente...")
            
            sinal = receber_dado(conn)
            if sinal == "SINCRONISMO_OK":
                print("Sinal recebido. Enviando resultado final...")
                enviar_dado(conn, resultado)
                print("Resultado enviado com sucesso!")

if __name__ == '__main__':
    porta_alvo = int(sys.argv[1]) if len(sys.argv) > 1 else 5001
    iniciar_servidor(porta_alvo)

