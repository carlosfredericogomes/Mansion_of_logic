import sys
import pygame

from config.config import (
    COR_BORDA, COR_BOTAO, COR_BOTAO_HOVER, FPS, IMAGENS_DIR, RESOLUTION,
    WHITE, WINDOW_TITLE,
)

MENU = "MENU"
JOGO = "JOGO"

BOTAO = pygame.Rect(0, 0, 260, 70)
BOTAO.center = (1090, 640)


def carregar_imagem(nome):
    return pygame.image.load(IMAGENS_DIR / nome).convert_alpha()


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
    tela = pygame.display.set_mode(RESOLUTION, pygame.SCALED | pygame.RESIZABLE)
    pygame.display.set_caption(WINDOW_TITLE)
    relogio = pygame.time.Clock()
    fonte = pygame.font.Font(None, 48)

    fundo = carregar_imagem("fundo_entrada_mansao.png")
    jogador = carregar_imagem("jogador_exterminador.png")
    
    jogador = pygame.transform.smoothscale(jogador, (154, 192))

    estado = MENU
    rodando = True
    while rodando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_F11:
                pygame.display.toggle_fullscreen()
            elif (estado == MENU and evento.type == pygame.MOUSEBUTTONDOWN
                  and evento.button == 1 and BOTAO.collidepoint(evento.pos)):
                estado = JOGO

        if estado == MENU:
            desenhar_menu(tela, fundo, jogador, fonte, pygame.mouse.get_pos())
        else:
    
            tela.fill((0, 0, 0))

        pygame.display.flip()
        relogio.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    menu_inicial()