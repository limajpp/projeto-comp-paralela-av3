import pandas as pd
import matplotlib.pyplot as plt
import os

def gerar_graficos():
    pasta_dados = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    os.makedirs(pasta_dados, exist_ok=True) 
    
    caminho_csv = os.path.join(pasta_dados, 'resultados_benchmark.csv')
    
    if not os.path.exists(caminho_csv):
        print(f"Erro: O arquivo {caminho_csv} não foi encontrado!")
        print("Rode o client.py primeiro para gerar os dados.")
        return
        
    df = pd.read_csv(caminho_csv)
    
    plt.style.use('seaborn-v0_8-darkgrid')
    
    plt.figure(figsize=(10, 6))
    df_serial = df[df['Workers'] == 1]
    plt.plot(df_serial['N'], df_serial['Tempo_Serial'], label='Serial (1 Núcleo)', color='black', linestyle='--', marker='o')
    
    cores = {1: 'red', 2: 'orange', 3: 'blue', 4: 'green'}
    for w in df['Workers'].unique():
        df_w = df[df['Workers'] == w]
        if w in cores:
            plt.plot(df_w['N'], df_w['Tempo_Distribuido'], label=f'Distribuído ({w} Servidores)', color=cores[w], marker='s')
        
    plt.title('Tempo de Execução: Serial vs Distribuído')
    plt.xlabel('Tamanho da Matriz (N x N)')
    plt.ylabel('Tempo (Segundos)')
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(pasta_dados, 'grafico_1_tempo_execucao.png'))
    plt.close()

    plt.figure(figsize=(10, 6))
    for w in df['Workers'].unique():
        if w == 1: continue 
        df_w = df[df['Workers'] == w]
        if w in cores:
            plt.plot(df_w['N'], df_w['Speedup'], label=f'{w} Servidores', color=cores[w], marker='^')
        
    plt.axhline(y=1, color='black', linestyle='--', label='Baseline (Sem ganho)')
    
    plt.title('Curva de Speedup por Tamanho de Matriz')
    plt.xlabel('Tamanho da Matriz (N x N)')
    plt.ylabel('Speedup (Vezes mais rápido)')
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(pasta_dados, 'grafico_2_speedup.png'))
    plt.close()

    print("Gráficos gerados com sucesso na pasta utils/data/ !")
    print("- utils/data/grafico_1_tempo_execucao.png")
    print("- utils/data/grafico_2_speedup.png")

if __name__ == '__main__':
    gerar_graficos()

