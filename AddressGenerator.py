import random

class AddressGenerator:
    def __init__(self, config, seed=None):
        self.config = config
        self.boundaries = config.get_segment_boundaries()
        if seed is not None:
            random.seed(seed)

    # -------------------------
    # Parser DEC + HEX + limpa BOM
    # -------------------------
    def _parse_address(self, text):
        text = text.strip()

        # Remove BOM / UTF-16 chars
        text = text.replace("\ufeff", "")
        text = text.replace("ÿ", "").replace("þ", "")

        # Hexadecimal
        if text.lower().startswith("0x"):
            return int(text, 16)

        # Decimal normal
        return int(text)

    # -------------------------
    # Salvar
    # -------------------------
    def save(self, addresses, filename):
        with open(filename, "w", encoding="utf-8") as f:
            for a in addresses:
                f.write(str(a) + "\n")

    # -------------------------
    # Carregar (agora com HEX)
    # -------------------------
    def load(self, filename):
        addrs = []
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    addrs.append(self._parse_address(line))
        return addrs
