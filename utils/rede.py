import struct
import pickle

def enviar_dado(conexao, dado):
    """Serializa o dado e envia com o tamanho no cabeçalho."""
    dado_bytes = pickle.dumps(dado)
    conexao.sendall(struct.pack('>I', len(dado_bytes)) + dado_bytes)

def receber_dado(conexao):
    """Lê o tamanho no cabeçalho e reagrupa os pacotes até formar o dado completo."""
    raw_msglen = _receber_todos_bytes(conexao, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    dado_bytes = _receber_todos_bytes(conexao, msglen)
    return pickle.loads(dado_bytes)

def _receber_todos_bytes(conexao, n):
    """Garante a leitura exata de 'n' bytes da rede."""
    dados = bytearray()
    while len(dados) < n:
        pacote = conexao.recv(n - len(dados))
        if not pacote:
            return None
        dados.extend(pacote)
    return dados

