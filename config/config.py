from pathlib import Path


RESOLUTION = (1280, 720)
WIDTH, HEIGHT = RESOLUTION
FPS = 60
WINDOW_TITLE = "Mansion of Logic"

BASE_DIR = Path(__file__).resolve().parent.parent
IMAGENS_DIR = BASE_DIR / "assets" / "imagens"
PERGUNTAS_DIR = BASE_DIR / "perguntas"


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

COR_BOTAO = (60, 30, 90)
COR_BOTAO_HOVER = (110, 60, 160)
COR_BORDA = (20, 16, 28)