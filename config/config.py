from pathlib import Path


RESOLUTION = (1280, 720)
WIDTH, HEIGHT = RESOLUTION
FPS = 60
WINDOW_TITLE = "Mansion of Logic"

BASE_DIR = Path(__file__).resolve().parent.parent
IMAGENS_DIR = BASE_DIR / "assets" / "imagens"
PERGUNTAS_DIR = BASE_DIR / "perguntas"
FONTES_DIR = BASE_DIR / "assets" / "fontes"
FONTE_PADRAO = "DejaVuSans.ttf"        # tem ∧ ∨ ¬ → ↔ (licença em assets/fontes/LICENSE-DejaVu.txt)
FONTE_NEGRITO = "DejaVuSans-Bold.ttf"


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

COR_BOTAO = (60, 30, 90)
COR_BOTAO_HOVER = (110, 60, 160)
COR_BORDA = (20, 16, 28)

# Telas de pergunta e combate
COR_PAINEL = (28, 22, 40)
COR_TEXTO = (240, 236, 245)
COR_SELECIONADA = (110, 60, 160)
COR_ACERTO = (46, 170, 80)
COR_ERRO = (205, 55, 55)
COR_CORACAO = (225, 50, 75)
COR_PLACEHOLDER = (120, 80, 160)