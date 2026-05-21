import os
import socket
import sys
from dotenv import load_dotenv
from utils.rede import receber_dado, enviar_dado
from utils.matrix import multiplicar_submatriz

def iniciar_servidor(porta):
    load_dotenv()
    HOST = os.getenv('HOST')
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, porta))
        s.listen(5)
        print(f"Servidor aguardando conexão na porta {porta}...")
        
        while True:
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

