import json
import warnings

from config.config import PERGUNTAS_DIR
from src.chefes import CHEFES

CAMPOS_OBRIGATORIOS = ("id", "enunciado", "opcoes", "correta", "explicacao")
MIN_OPCOES = 2
MAX_OPCOES = 4

def validar_pergunta(pergunta, origem="pergunta"):
    if not isinstance(pergunta, dict):
        raise ValueError(f"{origem}: cada pergunta deve ser um objeto JSON")
    for campo in CAMPOS_OBRIGATORIOS:
        if campo not in pergunta:
            raise ValueError(f"{origem}: falta o campo {campo}")

    opcoes = pergunta["opcoes"]
    if not isinstance(opcoes, list) or not all(isinstance(o, str) for o in opcoes):
        raise ValueError(f"{origem}: apcoes deve ser uma lista de textos")
    if not MIN_OPCOES <= len(opcoes) <= MAX_OPCOES:
        raise ValueError(f"{origem}: opcoes deve ter de {MIN_OPCOES} a {MAX_OPCOES} alternativas tem {len(opcoes)}")

    correta = pergunta["correta"]
    if isinstance(correta, bool) or not isinstance(correta, int) or not 0 <= correta < len(opcoes):
        raise ValueError(f"{origem}: correta ({correta!r}) deve ser uma posição de 0 a {len(opcoes) - 1 } em apcoes ")

def carregar_perguntas(andar): 
    caminho = PERGUNTAS_DIR / f"andar_{andar}.json"
    if not caminho.exists():
        warnings.warn(f"banco de perguntas não encontrado: {caminho}", UserWarning, stacklevel=2)
        return []

    with open(caminho, encoding="utf-8") as f:
        perguntas = json.load(f)
    if not isinstance(perguntas, list):
        raise ValueError(f"{caminho.name}: o arquivo deve conter uma lista de perguntas")

    for posicao, pergunta in enumerate(perguntas, start=1):
        validar_pergunta(pergunta, origem=f"{caminho.name}, perguta {posicao}")

    esperado = CHEFES.get(andar, {}).get("perguntas")
    if esperado is not None and len(perguntas) < esperado:
        warnings.warn(f"andar {andar}: o banco tem {len(perguntas)} perguntas, mas o esperado é {esperado}",UserWarning, stacklevel=2)
    return perguntas


NIVEIS_EXPLORACAO = (1, 2, 3)   # 1 fácil, 2 média, 3 difícil


def carregar_perguntas_exploracao(niveis=NIVEIS_EXPLORACAO):
    """Perguntas dos baús da exploração (perguntas/exploracao.json), só dos níveis pedidos.
    Cada pergunta tem, além dos campos de sempre, `nivel` (1 fácil, 2 média, 3 difícil)."""
    caminho = PERGUNTAS_DIR / "exploracao.json"
    if not caminho.exists():
        warnings.warn(f"banco de perguntas não encontrado: {caminho}", UserWarning, stacklevel=2)
        return []
    with open(caminho, encoding="utf-8") as f:
        perguntas = json.load(f)
    if not isinstance(perguntas, list):
        raise ValueError(f"{caminho.name}: o arquivo deve conter uma lista de perguntas")
    for posicao, pergunta in enumerate(perguntas, start=1):
        validar_pergunta(pergunta, origem=f"{caminho.name}, pergunta {posicao}")
        if pergunta.get("nivel") not in NIVEIS_EXPLORACAO:
            raise ValueError(f"{caminho.name}, pergunta {posicao}: nivel deve ser 1, 2 ou 3")
    return [p for p in perguntas if p["nivel"] in niveis]
