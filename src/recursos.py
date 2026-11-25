"""Carregamento de imagens e fontes com cache. Usa pygame (só a interface importa este módulo)."""
import pygame

from config.config import (
    COR_BORDA, COR_PLACEHOLDER, FONTE_NEGRITO, FONTE_PADRAO, FONTE_TERROR, FONTES_DIR, IMAGENS_DIR, SONS_DIR,
)

# Sons do jogo (arquivos em assets/sons).
SOM_ACERTO = "acerto.wav"
SOM_ERRO = "erro.wav"
SOM_VITORIA = "vitoria.wav"
SOM_GAME_OVER = "game_over.mp3"
SOM_PASSOS = ("passo_1.wav", "passo_2.wav", "passo_3.wav")  # variações, para não soar repetido

# Artes dos 4 andares: fundo do duelo e chefe de cada um.
FUNDOS_ANDAR = {1: "fundo_andar1.png", 2: "fundo_andar2.png", 3: "fundo_andar4.png", 4: "fundo_andar3.png"}
CHEFES_SPRITE = {1: "chefe_dracula.png", 2: "chefe_frankenstein.png", 3: "chefe_musashi.png", 4: "chefe_lobisomem.png"}
JOGADOR_SPRITE = "jogador_exterminador.png"
JOGADOR_COSTAS_SPRITE = "jogador_exterminador_costas.png"
JOGADOR_ESQUERDA_SPRITE = "jogador_exterminador_esquerda.png"
# Cenas da exploração de cada andar, na ordem em que o Exterminador passa por elas.
FUNDOS_EXPLORACAO = {
    1: ("fundo_exploracao_2_porta.png", "fundo_exploracao_3_salao.png", "fundo_exploracao_4_escada.png"),
    2: ("escada_frank.png", "corredor_frank.png"),
    3: ("escada_musashi.png", "corredor_musashi.png"),
    4: ("escada_lobisomen.png", "corredor_lobisomen.png"),
}

_cache_imagens = {}
_cache_fontes = {}
_cache_sons = {}
_mudo = False   # o menu de pausa (ESC) liga e desliga o som
_mixer_ok = None  # None = ainda não tentou iniciar o áudio


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


def carregar_fonte_terror(tamanho):
    """Fonte de terror (Creepster) do título do menu, em cache. Não tem acentos nem símbolos lógicos."""
    chave = ("terror", tamanho)
    if chave not in _cache_fontes:
        _cache_fontes[chave] = pygame.font.Font(FONTES_DIR / FONTE_TERROR, tamanho)
    return _cache_fontes[chave]


def carregar_fonte(tamanho, negrito=False):
    """Fonte TTF com os símbolos lógicos (DejaVu Sans), em cache por tamanho."""
    chave = (tamanho, negrito)
    if chave not in _cache_fontes:
        arquivo = FONTE_NEGRITO if negrito else FONTE_PADRAO
        _cache_fontes[chave] = pygame.font.Font(FONTES_DIR / arquivo, tamanho)
    return _cache_fontes[chave]

def _iniciar_audio():
    """Liga o áudio uma vez. Se o computador não tiver saída de som, o jogo segue mudo (sem travar)."""
    global _mixer_ok
    if _mixer_ok is None:
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            _mixer_ok = True
        except pygame.error as erro:
            print(f"[aviso] sem áudio ({erro}); o jogo continua sem som.")
            _mixer_ok = False
    return _mixer_ok


def som_mudo():
    return _mudo


def alternar_mudo():
    """Liga ou desliga todos os sons do jogo. Devolve True se ficou mudo."""
    global _mudo
    _mudo = not _mudo
    return _mudo


def tocar_som(nome):
    """Toca um som de assets/sons. Se faltar o arquivo ou o áudio, avisa no terminal e segue sem som."""
    if _mudo or not _iniciar_audio():
        return
    if nome not in _cache_sons:
        caminho = SONS_DIR / nome
        try:
            _cache_sons[nome] = pygame.mixer.Sound(caminho)
        except (pygame.error, FileNotFoundError):
            print(f"[aviso] som não encontrado ({nome}); seguindo sem ele.")
            _cache_sons[nome] = None
    if _cache_sons[nome] is not None:
        _cache_sons[nome].play()


def redimensionar_por_altura(img, altura):
    """Redimensiona mantendo a proporção da imagem."""
    largura = round(img.get_width() * altura / img.get_height())
    return pygame.transform.smoothscale(img, (largura, altura))