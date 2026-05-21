import socket
import time
import os
from dotenv import load_dotenv
from utils.matrix import gerar_matriz, multiplicacao_serial
from utils.rede import receber_dado, enviar_dado

load_dotenv()

HOST = os.getenv("HOST")
PORTA_BASE = 5001

def _ler_portas_servidores():
    entrada = input("Quantidade de servidores (ex: 2): ").strip()
    if not entrada:
        return [5001, 5002]
    quantidade = int(entrada)
    return list(range(PORTA_BASE, PORTA_BASE + quantidade))

def _ler_tamanhos_teste():
    entrada = input("Tamanhos de teste (ex: 100,250,500): ").strip()
    if not entrada:
        return [100, 250, 500, 750, 1000]
    return [int(valor.strip()) for valor in entrada.split(",") if valor.strip()]

def iniciar_cliente():
    portas_servidores = _ler_portas_servidores()
    tamanhos_teste = _ler_tamanhos_teste()
    resultados_tabela = [] 

    print(">>> INICIANDO BATERIA DE TESTES (SERIAL VS DISTRIBUÍDO) <<<\n")
    
    for N in tamanhos_teste:
        print("\n" + "="*50)
        print(f"=== TESTE PARA MATRIZ {N}x{N} ===")
        print("="*50)
        
        print(f"Gerando matrizes A e B ({N}x{N})...")
        matriz_A = gerar_matriz(N)
        matriz_B = gerar_matriz(N)
        
        print("\n>>> Iniciando cálculo SERIAL (Referência)...")
        inicio_serial = time.time()
        resultado_serial = multiplicacao_serial(matriz_A, matriz_B, N)
        tempo_serial = time.time() - inicio_serial
        print(f"Tempo SERIAL: {tempo_serial:.4f} segundos")

        print("\n>>> Iniciando processamento DISTRIBUÍDO (Sockets)...")
        inicio_distribuido = time.time()
        
        num_servers = len(portas_servidores)
        tamanho_fatia = N // num_servers
        conexoes = []
        
        for porta in portas_servidores:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((HOST, porta))
            conexoes.append(s)
            print(f"[+] Conectado ao servidor na porta {porta}")
        
        for i, conn in enumerate(conexoes):
            inicio_fatia = i * tamanho_fatia
            fim_fatia = N if i == num_servers - 1 else (i + 1) * tamanho_fatia
            sub_A = matriz_A[inicio_fatia:fim_fatia]
            
            pacote = {'sub_A': sub_A, 'B': matriz_B}
            enviar_dado(conn, pacote)
            print(f"[>] Dados enviados ao Servidor {i+1} (Linhas {inicio_fatia} a {fim_fatia-1})")
        
        print("\nAguardando o cálculo dos servidores na rede...")
        
        matriz_C_distribuida = []
        
        for i, conn in enumerate(conexoes):
            enviar_dado(conn, "SINCRONISMO_OK")
            sub_C = receber_dado(conn)
            matriz_C_distribuida.extend(sub_C)
            print(f"[<] Resultado recebido do Servidor {i+1} e concatenado.")
            conn.close()
            
        tempo_distribuido = time.time() - inicio_distribuido
        
        print(f"\nMatriz C gerada com sucesso! Possui {len(matriz_C_distribuida)} linhas.")
        print(f"Tempo DISTRIBUÍDO: {tempo_distribuido:.4f} segundos")

        consistente = resultado_serial == matriz_C_distribuida
        status_safety = "Sim" if consistente else "Não"
        print(f"Resultados Consistentes (Safety)? {status_safety}")
        
        speedup = tempo_serial / tempo_distribuido if tempo_distribuido > 0 else 0
        print(f"Speedup Alcançado: {speedup:.2f}x")
        
        resultados_tabela.append((N, tempo_serial, tempo_distribuido, speedup, status_safety))

    print("\n\n" + "#"*95)
    print("### RESUMO FINAL: BATERIA DE TESTES (BENCHMARK) ###")
    print("#"*95)
    print(f"{'Matriz (NxN)':<15} | {'Tempo Serial (s)':<20} | {'Tempo Distribuído (s)':<25} | {'Speedup':<10} | {'Safety'}")
    print("-" * 95)
    for res in resultados_tabela:
        n, t_ser, t_dist, spd, saf = res
        print(f"{n:<15} | {t_ser:<20.4f} | {t_dist:<25.4f} | {spd:<9.2f}x | {saf}")

if __name__ == '__main__':
    iniciar_cliente()

