import socket
import time
import os
import pandas as pd
from dotenv import load_dotenv
from utils.matrix import gerar_matriz, multiplicacao_serial
from utils.rede import receber_dado, enviar_dado

load_dotenv()
HOST = os.getenv("HOST", "127.0.0.1")
PORTA_BASE = 5001

def _ler_portas_servidores():
    entrada = input("Quantidade MÁXIMA de servidores rodando (ex: 4): ").strip()
    quantidade = int(entrada) if entrada else 4
    return list(range(PORTA_BASE, PORTA_BASE + quantidade))

def _ler_tamanhos_teste():
    entrada = input("Tamanhos de teste (ex: 100, 250, 500, 750, 1000): ").strip()
    if not entrada:
        return [100, 250, 500, 750, 1000]
    return [int(valor.strip()) for valor in entrada.split(",") if valor.strip()]

def iniciar_cliente():
    portas_disponiveis = _ler_portas_servidores()
    tamanhos_teste = _ler_tamanhos_teste()
    resultados_tabela = [] 

    print("\n>>> INICIANDO BATERIA MASSIVA DE TESTES (BENCHMARK) <<<")
    
    for N in tamanhos_teste:
        print("\n" + "="*50)
        print(f"=== TESTANDO MATRIZ {N}x{N} ===")
        print("="*50)
        
        print("Gerando matrizes A e B...")
        matriz_A = gerar_matriz(N)
        matriz_B = gerar_matriz(N)
        
        print("Calculando Baseline SERIAL (Referência)...")
        inicio_serial = time.time()
        multiplicacao_serial(matriz_A, matriz_B, N)
        tempo_serial = time.time() - inicio_serial
        print(f"Tempo SERIAL: {tempo_serial:.4f} segundos")

        for num_servers in range(1, len(portas_disponiveis) + 1):
            print(f"\n[>] Executando com {num_servers} Servidor(es)...")
            portas_ativas = portas_disponiveis[:num_servers]
            
            inicio_distribuido = time.time()
            tamanho_fatia = N // num_servers
            conexoes = []
            
            for porta in portas_ativas:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((HOST, porta))
                conexoes.append(s)
            
            for i, conn in enumerate(conexoes):
                inicio_fatia = i * tamanho_fatia
                fim_fatia = N if i == num_servers - 1 else (i + 1) * tamanho_fatia
                print(f"    [>] Enviando FATIA de A (Linhas {inicio_fatia} a {fim_fatia-1}) e MATRIZ B inteira ({N}x{N}) para Servidor {i+1}")
                pacote = {'sub_A': matriz_A[inicio_fatia:fim_fatia], 'B': matriz_B}
                enviar_dado(conn, pacote)
            
            matriz_C_distribuida = []
            for i, conn in enumerate(conexoes):
                enviar_dado(conn, "SINCRONISMO_OK")
                resultado_parcial = receber_dado(conn)
                print(f"    [<] Resultado recebido do Servidor {i+1} (Calculou {len(resultado_parcial)} linhas). Concatenando na Matriz C...")
                matriz_C_distribuida.extend(resultado_parcial)
                conn.close()
                
            tempo_distribuido = time.time() - inicio_distribuido
            
            speedup = tempo_serial / tempo_distribuido if tempo_distribuido > 0 else 0
            eficiencia = speedup / num_servers
            
            print(f"[<] Tempo Distribuído: {tempo_distribuido:.4f}s | Speedup: {speedup:.2f}x | Eficiência: {eficiencia:.2f}")
            
            resultados_tabela.append({
                'N': N, 
                'Workers': num_servers, 
                'Tempo_Serial': tempo_serial, 
                'Tempo_Distribuido': tempo_distribuido, 
                'Speedup': speedup, 
                'Eficiencia': eficiencia
            })

    pasta_saida = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'utils', 'data')
    os.makedirs(pasta_saida, exist_ok=True)
    
    caminho_csv = os.path.join(pasta_saida, 'resultados_benchmark.csv')
    df = pd.DataFrame(resultados_tabela)
    df.to_csv(caminho_csv, index=False)
    
    print("\n" + "#"*95)
    print("### RESUMO FINAL: BATERIA DE TESTES (BENCHMARK) ###")
    print("#"*95)
    print(df.to_string(index=False))
    
    print(f"\n[!] Dados exportados para 'utils/data/resultados_benchmark.csv'.")
    print("[!] Execute 'python graphics.py' para gerar os gráficos visuais.")

if __name__ == '__main__':
    iniciar_cliente()

