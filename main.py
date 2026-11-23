import sys
import pygame

from config.config import (
    ALTURA_JOGADOR_MEDIA, COR_BORDA, COR_BOTAO, COR_BOTAO_HOVER, FPS, RESOLUTION, WHITE, WINDOW_TITLE,
)

from src.progressao import ANDAR_CONCLUIDO, VITORIA, Partida
from src.recursos import JOGADOR_SPRITE, carregar_imagem, redimensionar_por_altura
from src.tela_conclusao import TelaConclusao
from src.telas import TelaAndarConcluido, TelaDuelo, TelaExploracao, TelaGameOver

# Telas do jogo.
MENU = "MENU"
EXPLORACAO = "EXPLORACAO"
JOGO = "JOGO"
ANDAR_FEITO = "ANDAR_FEITO"
GAME_OVER = "GAME_OVER"
CONCLUSAO = "CONCLUSAO"

BOTAO = pygame.Rect(0, 0, 260, 70)
BOTAO.center = (1090, 640)


def desenhar_menu(tela, fundo, jogador, fonte, mouse_pos):
    tela.blit(fundo, (0, 0))
    tela.blit(jogador, jogador.get_rect(midbottom=(430, 700)))

    cor = COR_BOTAO_HOVER if BOTAO.collidepoint(mouse_pos) else COR_BOTAO
    pygame.draw.rect(tela, cor, BOTAO, border_radius=10)
    pygame.draw.rect(tela, COR_BORDA, BOTAO, width=4, border_radius=10)
    texto = fonte.render("COMEÇAR", True, WHITE)
    tela.blit(texto, texto.get_rect(center=BOTAO.center))


def menu_inicial():
    pygame.init()
    # Abre em tela cheia (o jogo desenha em 1280x720 e o pygame escala). F11 volta para janela.
    tela = pygame.display.set_mode(RESOLUTION, pygame.SCALED | pygame.RESIZABLE | pygame.FULLSCREEN)
    pygame.display.set_caption(WINDOW_TITLE)
    relogio = pygame.time.Clock()
    fonte = pygame.font.Font(None, 48)

    fundo = carregar_imagem("fundo_entrada_mansao.png", RESOLUTION)
    jogador = redimensionar_por_altura(carregar_imagem(JOGADOR_SPRITE), ALTURA_JOGADOR_MEDIA)

    estado = MENU
    partida = None      # andar atual, estrelas e pontuação (progressao.py)
    atual = None        # a tela que está aparecendo (exploração, duelo, estrelas, game over ou vitória)
    dt = 0.0
    rodando = True
    while rodando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_F11:
                pygame.display.toggle_fullscreen()
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

        if estado != MENU:
            atual.atualizar(dt)

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
                atual = TelaExploracao(partida.andar_atual)
                estado = EXPLORACAO
        elif estado in (GAME_OVER, CONCLUSAO) and atual.concluida:
            estado = MENU
            atual = None
            partida = None

        if estado == MENU:
            desenhar_menu(tela, fundo, jogador, fonte, pygame.mouse.get_pos())
        else:
            atual.desenhar(tela)

        pygame.display.flip()
        dt = min(relogio.tick(FPS) / 1000, 0.1)  # segundos desde o quadro anterior (limitado)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    menu_inicial()
