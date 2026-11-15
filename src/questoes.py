import json
import random
from config.config import PERGUNTAS_DIR


def carregar_perguntas(andar):
    caminho = PERGUNTAS_DIR / f"andar_{andar}.json"
    with open(caminho, encoding="utf-8") as f:
        perguntas = json.load(f)
    random.shuffle(perguntas)
    return perguntas
