"""Carregamento de imagens e fontes com cache. Usa pygame (só a interface importa este módulo)."""
import pygame

from config.config import COR_BORDA, COR_PLACEHOLDER, FONTE_NEGRITO, FONTE_PADRAO, FONTES_DIR, IMAGENS_DIR

# Artes incorporadas nesta etapa (andares 1 e 2). Os outros andares usam retângulo provisório.
FUNDOS_ANDAR = {1: "fundo_andar1.png", 2: "fundo_andar2.png"}
CHEFES_SPRITE = {1: "chefe_lobisomem.png", 2: "chefe_frankenstein.png"}
JOGADOR_SPRITE = "jogador_exterminador.png"
JOGADOR_COSTAS_SPRITE = "jogador_exterminador_costas.png"
# Cenas da caminhada até o primeiro confronto, na ordem (porta, salão e escada).
FUNDOS_EXPLORACAO = (
    "fundo_exploracao_2_porta.png",
    "fundo_exploracao_3_salao.png",
    "fundo_exploracao_4_escada.png",
)

_cache_imagens = {}
_cache_fontes = {}


def _retangulo_provisorio(tamanho):
    superficie = pygame.Surface(tamanho, pygame.SRCALPHA)
    pygame.draw.rect(superficie, COR_PLACEHOLDER, superficie.get_rect(), border_radius=12)
    pygame.draw.rect(superficie, COR_BORDA, superficie.get_rect(), width=4, border_radius=12)
    return superficie


def carregar_imagem(nome, tamanho=None):
    """Carrega uma imagem de assets/imagens (com convert_alpha e cache).

    `tamanho` redimensiona. Se o arquivo não existir (ou nome for None), devolve um
    retângulo provisório e mostra um aviso no terminal, em vez de travar o jogo.
    """
    chave = (nome, tamanho)
    if chave in _cache_imagens:
        return _cache_imagens[chave]

    caminho = IMAGENS_DIR / nome if nome else None
    if caminho is not None and caminho.exists():
        imagem = pygame.image.load(caminho).convert_alpha()
        if tamanho is not None:
            imagem = pygame.transform.smoothscale(imagem, tamanho)
    else:
        print(f"[aviso] imagem não encontrada ({nome}); usando retângulo provisório.")
        imagem = _retangulo_provisorio(tamanho or (200, 240))

    _cache_imagens[chave] = imagem
    return imagem


def carregar_fonte(tamanho, negrito=False):
    """Fonte TTF com os símbolos lógicos (DejaVu Sans), em cache por tamanho."""
    chave = (tamanho, negrito)
    if chave not in _cache_fontes:
        arquivo = FONTE_NEGRITO if negrito else FONTE_PADRAO
        _cache_fontes[chave] = pygame.font.Font(FONTES_DIR / arquivo, tamanho)
    return _cache_fontes[chave]

def redimensionar_por_altura(img, altura):
    """Redimensiona mantendo a proporção da imagem."""
    largura = round(img.get_width() * altura / img.get_height())
    return pygame.transform.smoothscale(img, (largura, altura))