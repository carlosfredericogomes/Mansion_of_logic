import sys
import pygame

from config.config import (
    COR_BORDA, COR_BOTAO, COR_BOTAO_HOVER, FPS, RESOLUTION, WHITE, WINDOW_TITLE,
)
from src.recursos import JOGADOR_SPRITE, carregar_imagem
from src.regras import Duelo
from src.telas import TelaDuelo, TelaExploracao

MENU = "MENU"
EXPLORACAO = "EXPLORACAO"
JOGO = "JOGO"

ANDAR_INICIAL = 1

BOTAO = pygame.Rect(0, 0, 260, 70)
BOTAO.center = (1090, 640)


def desenhar_menu(tela, fundo, jogador, fonte, mouse_pos):
    tela.blit(fundo, (0, 0))
    tela.blit(jogador, jogador.get_rect(midbottom=(640, 710)))

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

    fundo = carregar_imagem("fundo_entrada_mansao.png")
    # Exterminador reduzido (256x320 -> 154x192) para não cobrir a porta da mansão.
    jogador = carregar_imagem(JOGADOR_SPRITE, (154, 192))

    estado = MENU
    tela_exploracao = None
    tela_duelo = None
    dt = 0.0
    rodando = True
    while rodando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_F11:
                pygame.display.toggle_fullscreen()
            elif estado == MENU:
                if (evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1
                        and BOTAO.collidepoint(evento.pos)):
                    tela_exploracao = TelaExploracao()  # S0: o Exterminador caminha até o chefe
                    estado = EXPLORACAO
            elif estado == EXPLORACAO:
                tela_exploracao.tratar_evento(evento)
            elif estado == JOGO:
                tela_duelo.tratar_evento(evento)

        if estado == EXPLORACAO:
            tela_exploracao.atualizar(dt)
            if tela_exploracao.concluida:
                # Encontro com o chefe: o Duelo começa em S1 (ENCONTRO_CHEFE).
                tela_duelo = TelaDuelo(Duelo(ANDAR_INICIAL))
                tela_exploracao = None
                estado = JOGO
        elif estado == JOGO:
            tela_duelo.atualizar(dt)
            if tela_duelo.concluida:
                # Provisório: vitória (S5) e game over (S6) ainda não têm tela própria
                # (c15 e c18). Por enquanto, ao fim do duelo o jogo volta ao menu.
                estado = MENU
                tela_duelo = None

        if estado == MENU:
            desenhar_menu(tela, fundo, jogador, fonte, pygame.mouse.get_pos())
        elif estado == EXPLORACAO:
            tela_exploracao.desenhar(tela)
        else:
            tela_duelo.desenhar(tela)

        pygame.display.flip()
        dt = min(relogio.tick(FPS) / 1000, 0.1)  # segundos desde o quadro anterior (limitado)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    menu_inicial()
