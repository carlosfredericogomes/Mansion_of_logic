import math
import pygame

from config.config import COR_PAINEL, COR_TEXTO, HEIGHT, RESOLUTION, WIDTH
from src.recursos import JOGADOR_SPRITE, carregar_fonte, carregar_imagem
from src.telas import ENTER, _sprite_com_pivo_nos_pes, _suave

COR_OURO = (255, 214, 102)

FUNDO = "fundo_entrada_mansao.png"
TITULO = "VOCÊ ESCAPOU DA MANSÃO!"
SUBTITULO = "Os quatro chefes foram derrotados. A lógica venceu."
INTEGRANTES = (
    "Carlos Frederico Gomes",
    "Francisco Freitas",
    "Maria Carolina Belém",
    "Maria Giulia Castro",
)

TEMPO_ANDAR = 4.0
ATRASO_TEXTO = 0.3
FADE_TEXTO = 1.2
ATRASO_MENSAGEM = 1.0

X_CAMINHO = 640
PORTA_Y = 492
CHAO_Y = 702
ESCALA_PORTA = 0.27
ALTURA_EXPLORADOR = 300
PASSOS_POR_SEGUNDO = 3.2

PAINEL = pygame.Rect(880, 318, 370, 310)
ALTURA_FAIXA = 190
ESCURECER_FUNDO = 55


def _centralizado(superficie, texto, fonte, cor, x, y_topo, sombra=False):
    if sombra:
        escuro = fonte.render(texto, True, (0, 0, 0))
        superficie.blit(escuro, escuro.get_rect(midtop=(x + 2, y_topo + 3)))
    imagem = fonte.render(texto, True, cor)
    superficie.blit(imagem, imagem.get_rect(midtop=(x, y_topo)))


class TelaConclusao:
    def __init__(self):
        self.concluida = False
        self.acao = None
        self.tempo = 0.0
        self.fonte_mensagem = carregar_fonte(28)
        self.fundo = self._montar_fundo()
        self.sprite = _sprite_com_pivo_nos_pes(carregar_imagem(JOGADOR_SPRITE), ALTURA_EXPLORADOR)
        self.camada_texto = self._montar_camada_texto()

    @staticmethod
    def _montar_fundo():
        fundo = carregar_imagem(FUNDO, (WIDTH, HEIGHT)).copy()
        escuro = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        escuro.fill((0, 0, 0, ESCURECER_FUNDO))
        fundo.blit(escuro, (0, 0))
        return fundo

    @staticmethod
    def _montar_camada_texto():
        camada = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

        for y in range(ALTURA_FAIXA):
            alfa = int(215 * (1 - y / ALTURA_FAIXA) ** 1.3)
            pygame.draw.line(camada, (8, 6, 16, alfa), (0, y), (WIDTH, y))

        _centralizado(camada, TITULO, carregar_fonte(58, negrito=True), COR_OURO, WIDTH // 2, 26, sombra=True)
        _centralizado(camada, SUBTITULO, carregar_fonte(26), COR_TEXTO, WIDTH // 2, 100, sombra=True)

        pygame.draw.rect(camada, COR_PAINEL + (232,), PAINEL, border_radius=14)
        pygame.draw.rect(camada, COR_OURO, PAINEL, width=3, border_radius=14)
        meio = PAINEL.centerx
        _centralizado(camada, "DESENVOLVIDO POR", carregar_fonte(19, negrito=True), COR_OURO, meio, PAINEL.y + 24)
        pygame.draw.line(camada, COR_OURO + (150,), (PAINEL.x + 50, PAINEL.y + 62),
                         (PAINEL.right - 50, PAINEL.y + 62), 2)
        for i, nome in enumerate(INTEGRANTES):
            tamanho = 24
            fonte = carregar_fonte(tamanho)
            while fonte.size(nome)[0] > PAINEL.width - 44 and tamanho > 12:
                tamanho -= 1
                fonte = carregar_fonte(tamanho)
            _centralizado(camada, nome, fonte, COR_TEXTO, meio, PAINEL.y + 86 + i * 43)
        _centralizado(camada, "Mansion of Logic", carregar_fonte(18, negrito=True), COR_OURO, meio,
                      PAINEL.bottom - 38)
        return camada

    @property
    def andando(self):
        return self.tempo < TEMPO_ANDAR

    @property
    def opacidade_texto(self):
        return int(255 * _suave((self.tempo - TEMPO_ANDAR - ATRASO_TEXTO) / FADE_TEXTO))

    @property
    def mensagem_visivel(self):
        return self.tempo >= TEMPO_ANDAR + ATRASO_TEXTO + FADE_TEXTO + ATRASO_MENSAGEM

    def posicao_explorador(self):
        u = _suave(self.tempo / TEMPO_ANDAR)
        y = PORTA_Y + (CHAO_Y - PORTA_Y) * u
        escala = ESCALA_PORTA + (1.0 - ESCALA_PORTA) * u
        return X_CAMINHO, y, escala

    def tratar_evento(self, evento):
        if evento.type == pygame.KEYDOWN and evento.key in ENTER and self.mensagem_visivel:
            self.acao = "menu"
            self.concluida = True

    def atualizar(self, dt):
        self.tempo += dt

    def desenhar(self, tela):
        tela.blit(self.fundo, (0, 0))

        x, y, escala = self.posicao_explorador()
        angulo = 0.0
        if self.andando:
            fase = self.tempo * PASSOS_POR_SEGUNDO * math.pi
            angulo = 3.0 * math.sin(fase)
            escala *= 1.0 + 0.03 * abs(math.sin(fase))

        sombra = pygame.Surface((max(8, round(170 * escala)), max(4, round(32 * escala))), pygame.SRCALPHA)
        pygame.draw.ellipse(sombra, (0, 0, 0, 120), sombra.get_rect())
        tela.blit(sombra, sombra.get_rect(center=(round(x), round(y) - 2)))

        figura = pygame.transform.rotozoom(self.sprite, angulo, escala)
        tela.blit(figura, figura.get_rect(center=(round(x), round(y))))

        opacidade = self.opacidade_texto
        if opacidade > 0:
            self.camada_texto.set_alpha(opacidade)
            tela.blit(self.camada_texto, (0, 0))

        if self.mensagem_visivel:
            texto = "Aperte enter para voltar ao menu"
            escuro = self.fonte_mensagem.render(texto, True, (0, 0, 0))
            tela.blit(escuro, escuro.get_rect(bottomright=(WIDTH - 30, HEIGHT - 25)))
            imagem = self.fonte_mensagem.render(texto, True, COR_TEXTO)
            tela.blit(imagem, imagem.get_rect(bottomright=(WIDTH - 32, HEIGHT - 28)))


def visualizar():
    pygame.init()
    tela = pygame.display.set_mode(RESOLUTION)
    pygame.display.set_caption("Tela de conclusão")
    relogio = pygame.time.Clock()
    conclusao = TelaConclusao()
    rodando = True
    while rodando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT or (evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE):
                rodando = False
            else:
                conclusao.tratar_evento(evento)
        conclusao.atualizar(min(relogio.tick(60) / 1000, 0.1))
        if conclusao.concluida:
            conclusao = TelaConclusao()
        conclusao.desenhar(tela)
        pygame.display.flip()
    pygame.quit()


if __name__ == "__main__":
    visualizar()
