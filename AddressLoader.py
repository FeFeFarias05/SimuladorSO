import random

class AddressLoader:
    def __init__(self, config, seed=None):
        self.config = config
        self.limites = config.getLimitesSegmentos()
        if seed is not None:
            random.seed(seed)

    def processarEndereco(self, text):
        text = text.strip()

        text = text.replace("\ufeff", "")
        text = text.replace("ÿ", "").replace("þ", "")

        if text.lower().startswith("0x"):
            return int(text, 16)

        return int(text)

    def salvar(self, enderecos, nome_arquivo):
        with open(nome_arquivo, "w", encoding="utf-8") as f:
            for endereco in enderecos:
                f.write(str(endereco) + "\n")

    def carregar(self, nomeArquivo):
        enderecos = []
        with open(nomeArquivo, "r", encoding="utf-8") as f:
            for linha in f:
                linha = linha.strip()
                if linha:
                    enderecos.append(self.processarEndereco(linha))
        return enderecos
