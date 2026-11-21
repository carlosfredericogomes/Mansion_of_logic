import sys
import pygame

from config.config import (
    ALTURA_JOGADOR_MEDIA, COR_BORDA, COR_BOTAO, COR_BOTAO_HOVER, FPS, RESOLUTION, WHITE, WINDOW_TITLE,
)

from src.regras import Duelo
from src.telas import TelaDuelo, TelaExploracao, TelaGameOver
from src.recursos import JOGADOR_SPRITE, carregar_imagem, redimensionar_por_altura
from src.chefes import TOTAL_ANDARES


MENU = "MENU"
EXPLORACAO = "EXPLORACAO"
JOGO = "JOGO"
GAME_OVER = "GAME_OVER"

ANDAR_INICIAL = 1

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

    fundo = carregar_imagem("fundo_entrada_mansao.png", RESOLUTION)    # Exterminador reduzido (256x320 -> 154x192) para não cobrir a porta da mansão.
    jogador = redimensionar_por_altura(carregar_imagem(JOGADOR_SPRITE), ALTURA_JOGADOR_MEDIA)

    estado = MENU
    tela_exploracao = None
    tela_duelo = None
    tela_gameover = None
    duelo = None
    andar = ANDAR_INICIAL
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
                    andar = ANDAR_INICIAL
                    tela_exploracao = TelaExploracao(andar)  # S0: o Exterminador caminha até o chefe
                    estado = EXPLORACAO
            elif estado == EXPLORACAO:
                tela_exploracao.tratar_evento(evento)
            elif estado == JOGO:
                tela_duelo.tratar_evento(evento)
            elif estado == GAME_OVER:
                tela_gameover.tratar_evento(evento)

        if estado == EXPLORACAO:
            tela_exploracao.atualizar(dt)
            if tela_exploracao.concluida:
                # Encontro com o chefe: o Duelo começa em S1 (ENCONTRO_CHEFE).
                duelo = Duelo(andar)
                tela_duelo = TelaDuelo(duelo)                
                tela_exploracao = None
                estado = JOGO
        elif estado == JOGO:
            tela_duelo.atualizar(dt)
            if tela_duelo.concluida:
                if duelo.game_over:
                    tela_gameover = TelaGameOver()
                    estado = GAME_OVER
                    tela_duelo = None
                elif andar < TOTAL_ANDARES:
                    andar += 1
                    tela_exploracao = TelaExploracao(andar)   # sobe a escada e anda pelo corredor
                    tela_duelo = None
                    estado = EXPLORACAO
                else:
                    estado = MENU   # provisório: zerou o jogo (ainda não existe tela de vitória)
                    tela_duelo = None
        elif estado == GAME_OVER:
            tela_gameover.atualizar(dt)
            if tela_gameover.concluida:
                if tela_gameover.acao == "tentar_novamente":
                    duelo = Duelo(duelo.andar)
                    tela_duelo = TelaDuelo(duelo)
                    estado = JOGO
                else:
                    estado = MENU
                tela_gameover = None

        if estado == MENU:
            desenhar_menu(tela, fundo, jogador, fonte, pygame.mouse.get_pos())
        elif estado == EXPLORACAO:
            tela_exploracao.desenhar(tela)
        elif estado == GAME_OVER:
            tela_gameover.desenhar(tela)
        else:
            tela_duelo.desenhar(tela)

        pygame.display.flip()
        dt = min(relogio.tick(FPS) / 1000, 0.1)  # segundos desde o quadro anterior (limitado)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    menu_inicial()
