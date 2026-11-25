import sys
import pygame

from config.config import (
    ALTURA_JOGADOR_MEDIA, COR_BORDA, COR_BOTAO, COR_BOTAO_HOVER, COR_TITULO, FPS, RESOLUTION, WHITE, WINDOW_TITLE,
)

from src.progressao import ANDAR_CONCLUIDO, VITORIA, Partida
from src.recursos import (
    JOGADOR_SPRITE, alternar_mudo, carregar_fonte_terror, carregar_imagem, redimensionar_por_altura,
)
from src.tela_conclusao import TelaConclusao
from src.telas import (
    TelaAndarConcluido, TelaBau, TelaDuelo, TelaExploracao, TelaGameOver, TelaPausa, desenhar_dica,
)

# Telas do jogo.
MENU = "MENU"
EXPLORACAO = "EXPLORACAO"
JOGO = "JOGO"
ANDAR_FEITO = "ANDAR_FEITO"
GAME_OVER = "GAME_OVER"
CONCLUSAO = "CONCLUSAO"

DICA_MENU = ("Enter ou clique: começar   ·   W A S D / setas: andar   ·   1 a 4 e Enter: responder"
             "   ·   ESC: pausa   ·   F11: tela cheia")
JOGANDO = (EXPLORACAO, JOGO, ANDAR_FEITO)   # estados em que o ESC abre a pausa

NOME_DO_JOGO = "Mansion Of Logic"
TITULO_TAMANHO = 120
TITULO_CENTRO_Y = 78

BOTAO = pygame.Rect(0, 0, 260, 70)
BOTAO.center = (1090, 640)


def montar_titulo():
    """Nome do jogo em fonte de terror, letras vermelhas com contorno escuro e um brilho sangrento atrás.
    Montado uma vez (as letras não mudam), para o menu só copiar a imagem a cada quadro."""
    fonte = carregar_fonte_terror(TITULO_TAMANHO)
    letras = fonte.render(NOME_DO_JOGO, True, COR_TITULO)
    contorno = fonte.render(NOME_DO_JOGO, True, (22, 4, 8))
    brilho = fonte.render(NOME_DO_JOGO, True, (150, 0, 10))
    margem = 24
    largura, altura = letras.get_width() + 2 * margem, letras.get_height() + 2 * margem
    imagem = pygame.Surface((largura, altura), pygame.SRCALPHA)
    halo = pygame.Surface((largura, altura), pygame.SRCALPHA)
    halo.blit(brilho, (margem, margem))
    pequeno = pygame.transform.smoothscale(halo, (largura // 6, altura // 6))
    halo = pygame.transform.smoothscale(pequeno, (largura, altura))      # desfoca, para virar um brilho
    for _ in range(3):
        imagem.blit(halo, (0, 0))
    for dx in range(-4, 5):                                              # contorno escuro de 4 px
        for dy in range(-4, 5):
            if dx * dx + dy * dy <= 16:
                imagem.blit(contorno, (margem + dx, margem + dy + 4))
    imagem.blit(letras, (margem, margem))
    return imagem


def desenhar_menu(tela, fundo, jogador, fonte, mouse_pos, titulo=None):
    tela.blit(fundo, (0, 0))
    if titulo is not None:
        tela.blit(titulo, titulo.get_rect(center=(640, TITULO_CENTRO_Y)))
    tela.blit(jogador, jogador.get_rect(midbottom=(430, 700)))

    cor = COR_BOTAO_HOVER if BOTAO.collidepoint(mouse_pos) else COR_BOTAO
    pygame.draw.rect(tela, cor, BOTAO, border_radius=10)
    pygame.draw.rect(tela, COR_BORDA, BOTAO, width=4, border_radius=10)
    texto = fonte.render("COMEÇAR", True, WHITE)
    tela.blit(texto, texto.get_rect(center=BOTAO.center))
    desenhar_dica(tela, DICA_MENU, (640, 690), tamanho=18)


def menu_inicial():
    pygame.init()
    # Abre em tela cheia (o jogo desenha em 1280x720 e o pygame escala). F11 volta para janela.
    tela = pygame.display.set_mode(RESOLUTION, pygame.SCALED | pygame.RESIZABLE | pygame.FULLSCREEN)
    pygame.display.set_caption(WINDOW_TITLE)
    relogio = pygame.time.Clock()
    fonte = pygame.font.Font(None, 48)
    titulo = montar_titulo()

    fundo = carregar_imagem("fundo_entrada_mansao.png", RESOLUTION)
    jogador = redimensionar_por_altura(carregar_imagem(JOGADOR_SPRITE), ALTURA_JOGADOR_MEDIA)

    estado = MENU
    partida = None      # andar atual, estrelas e pontuação (progressao.py)
    atual = None        # a tela que está aparecendo (exploração, duelo, estrelas, game over ou vitória)
    pausa = None        # menu de pausa (ESC), quando aberto
    bau = None          # pergunta do baú da exploração, quando aberta
    dt = 0.0
    rodando = True
    
    while rodando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_F11:
                pygame.display.toggle_fullscreen()
            elif pausa is not None:
                acao = pausa.tratar_evento(evento)
                if acao == "continuar":
                    pausa = None
                elif acao == "som":
                    alternar_mudo()
                elif acao == "menu":                   # abandona a partida e volta ao menu
                    pausa, bau, estado, atual, partida = None, None, MENU, None, None
                elif acao == "sair":
                    rodando = False
            elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE and estado in JOGANDO:
                pausa = TelaPausa()
            elif bau is not None:
                bau.tratar_evento(evento)
            elif estado == MENU:
                clicou = (evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1
                          and BOTAO.collidepoint(evento.pos))
                apertou_enter = evento.type == pygame.KEYDOWN and evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER)
                if clicou or apertou_enter:
                    partida = Partida()
                    atual = TelaExploracao(partida.andar_atual)  # S0: o Exterminador caminha até o chefe
                    estado = EXPLORACAO
            else:
                atual.tratar_evento(evento)

        if estado != MENU and pausa is None and bau is None:   # na pausa e na pergunta do baú o jogo fica congelado
            atual.atualizar(dt)
        elif bau is not None and pausa is None:   # só a pergunta do baú anda (a exploração fica parada atrás)
            bau.atualizar(dt)

        if estado == EXPLORACAO and bau is None and atual.pedir_bau:   # o jogador clicou em ABRIR no baú
            atual.pedir_bau = False
            bau = TelaBau(partida.sortear_pergunta_bau())
        elif bau is not None and bau.concluida:                        # fechou o resultado do baú
            partida.abrir_bau(bau.acertou)
            atual.bau_resolvido(bau.acertou)
            bau = None

        if estado == EXPLORACAO and atual.concluida:
            # Encontro com o chefe: o Duelo começa em S1 (ENCONTRO_CHEFE) com os 3 corações cheios.
            atual = TelaDuelo(partida.iniciar_duelo())
            estado = JOGO
        elif estado == JOGO and atual.concluida:
            if partida.concluir_duelo() == ANDAR_CONCLUIDO:   # venceu o chefe: mostra as estrelas
                atual = TelaAndarConcluido(partida.andar_atual, partida.ultimas_estrelas,
                                           partida.melhor_do_andar, partida.pode_repetir)
                estado = ANDAR_FEITO
            else:                                              # os corações acabaram
                atual = TelaGameOver()
                estado = GAME_OVER
        elif estado == ANDAR_FEITO and atual.concluida:
            if atual.acao == "repetir":                        # outra chance contra o mesmo chefe
                atual = TelaDuelo(partida.iniciar_duelo())
                estado = JOGO
            elif partida.avancar() == VITORIA:                 # derrotou o último chefe
                atual = TelaConclusao(partida.pontuacao_final)
                estado = CONCLUSAO
            else:                                              # sobe para o próximo andar
                atual = TelaExploracao(partida.andar_atual, partida.andar_tem_bau)
                estado = EXPLORACAO
        elif estado in (GAME_OVER, CONCLUSAO) and atual.concluida:
            estado = MENU
            atual = None
            partida = None

        if estado == MENU:
            desenhar_menu(tela, fundo, jogador, fonte, pygame.mouse.get_pos(), titulo)
        else:
            atual.desenhar(tela)
        if bau is not None:
            bau.desenhar(tela)
        if pausa is not None:
            pausa.desenhar(tela)

        pygame.display.flip()
        dt = min(relogio.tick(FPS) / 1000, 0.1)  # segundos desde o quadro anterior (limitado)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    menu_inicial()
