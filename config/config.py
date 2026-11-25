from pathlib import Path


RESOLUTION = (1280, 720)
WIDTH, HEIGHT = RESOLUTION
FPS = 60
WINDOW_TITLE = "Mansion of Logic"

BASE_DIR = Path(__file__).resolve().parent.parent
IMAGENS_DIR = BASE_DIR / "assets" / "imagens"
PERGUNTAS_DIR = BASE_DIR / "perguntas"
FONTES_DIR = BASE_DIR / "assets" / "fontes"
SONS_DIR = BASE_DIR / "assets" / "sons"
FONTE_PADRAO = "DejaVuSans.ttf"        # tem ∧ ∨ ¬ → ↔ (licença em assets/fontes/LICENSE-DejaVu.txt)
FONTE_NEGRITO = "DejaVuSans-Bold.ttf"
FONTE_TERROR = "Creepster-Regular.ttf"   # só para o título do menu (licença OFL em assets/fontes/LICENSE-Creepster.txt)


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)


# Telas de pergunta e combate
ALTURA_JOGADOR_MEDIA = 300      # altura (px) do Exterminador no menu e no combate

COR_PAINEL = (28, 22, 40)
COR_TEXTO = (240, 236, 245)
COR_SELECIONADA = (110, 60, 160)
COR_ACERTO = (46, 170, 80)
COR_ERRO = (205, 55, 55)
COR_CORACAO = (225, 50, 75)
COR_PLACEHOLDER = (120, 80, 160)
COR_DANO = (150, 0, 0)         # somada ao personagem que leva dano (piscada vermelha)
COR_TITULO = (200, 18, 28)       # letras vermelhas do título do menu
COR_GAME_OVER = (215, 25, 35)   # letras da tela de Game Over
COR_OURO = (255, 214, 102)      # estrelas e destaques da vitória
# ------------------------------------------------------------------------------

COR_BOTAO = (60, 30, 90)
COR_BOTAO_HOVER = (110, 60, 160)
COR_BORDA = (20, 16, 28)