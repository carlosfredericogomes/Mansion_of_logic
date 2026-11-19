"""Telas de exploração, pergunta e combate (pygame). Só desenham e leem o teclado:
quem decide o dano é o Duelo, em regras.py."""
import math

import pygame

from config.config import (
    COR_ACERTO, COR_BORDA, COR_CORACAO, COR_ERRO, COR_PAINEL, COR_SELECIONADA, COR_TEXTO,
    HEIGHT, WIDTH, COR_BOTAO, COR_BOTAO_HOVER, WHITE
)
from src.recursos import (
    CHEFES_SPRITE, FUNDOS_ANDAR, FUNDOS_EXPLORACAO, JOGADOR_COSTAS_SPRITE, JOGADOR_SPRITE,
    carregar_fonte, carregar_imagem, redimensionar_por_altura
)
from src.chefes import CHEFES

FASE_PERGUNTA = "PERGUNTA"
FASE_FEEDBACK = "FEEDBACK"

ENTER = (pygame.K_RETURN, pygame.K_KP_ENTER)

# --- Combate ---
TAMANHO_JOGADOR = (192, 240)
TAMANHO_CHEFE = (288, 336)
JOGADOR_X = 170
CHEFE_X = 1100
CHAO_Y = 650  # onde os pés dos personagens tocam o chão

PAINEL = pygame.Rect(340, 86, 600, 470)  # pergunta no meio da tela
PAINEL_MARGEM = 20
OPCAO_ALTURA = 40
OPCAO_ESPACO = 46
FLASH_TEMPO = 0.9      # segundos em que a alternativa pisca depois de responder
FLASH_PERIODO = 0.12   # duração de cada "aceso" e "apagado"
ESPERA_MINIMA = 0.6    # só dá para continuar depois que a piscada foi vista

# --- Exploração: (x, y dos pés, escala do sprite) no início e no fim de cada cena ---
CENAS = (
    {"duracao": 3.2, "ini": (640, 700, 0.75), "fim": (640, 548, 0.40)},   # porta
    {"duracao": 3.6, "ini": (640, 705, 0.70), "fim": (640, 528, 0.30)},   # salão
    {"duracao": 5.5, "ini": (640, 710, 0.70), "fim": (640, 378, 0.22)},   # escada
)
FADE_TEMPO = 0.4
PASSOS_POR_SEGUNDO = 3.2  # cada passo = um balanço do corpo


def quebrar_texto(texto, fonte, largura_max):
    """Quebra `texto` em linhas que cabem em `largura_max` pixels, cortando nos espaços.
    Uma palavra maior que a largura é cortada por caractere."""
    linhas = []
    atual = ""
    for palavra in texto.split():
        candidata = palavra if not atual else f"{atual} {palavra}"
        if fonte.size(candidata)[0] <= largura_max:
            atual = candidata
            continue
        if atual:
            linhas.append(atual)
        atual = ""
        while fonte.size(palavra)[0] > largura_max:  # palavra longa demais
            corte = len(palavra) - 1
            while corte > 1 and fonte.size(palavra[:corte])[0] > largura_max:
                corte -= 1
            linhas.append(palavra[:corte])
            palavra = palavra[corte:]
        atual = palavra
    if atual:
        linhas.append(atual)
    return linhas


def desenhar_coracao(superficie, centro, tamanho, cor):
    """Coração inteiro (dois círculos e um triângulo) com contorno escuro."""
    cx, cy = centro
    for extra, cor_atual in ((3, COR_BORDA), (0, cor)):
        t = tamanho + extra * 2
        r = t // 4
        pygame.draw.circle(superficie, cor_atual, (cx - r, cy - r // 2), r + 1)
        pygame.draw.circle(superficie, cor_atual, (cx + r, cy - r // 2), r + 1)
        pygame.draw.polygon(superficie, cor_atual, [
            (cx - t // 2 + 1, cy - r // 2 + 2), (cx + t // 2 - 1, cy - r // 2 + 2), (cx, cy + t // 2),
        ])


def _texto(superficie, texto, fonte, cor, pos, centro=False, direita=False):
    imagem = fonte.render(texto, True, cor)
    rect = imagem.get_rect()
    if centro:
        rect.center = pos
    elif direita:
        rect.topright = pos
    else:
        rect.topleft = pos
    superficie.blit(imagem, rect)
    return rect


def _linhas(superficie, linhas, fonte, cor, x, y, espaco, max_linhas):
    for i, linha in enumerate(linhas[:max_linhas]):
        _texto(superficie, linha, fonte, cor, (x, y + i * espaco))
    return y + min(len(linhas), max_linhas) * espaco


def _sprite_com_pivo_nos_pes(imagem):
    """Recorta as margens transparentes e devolve uma superfície com o centro nos pés.
    Assim, girar e escalar (rotozoom) mantém os pés parados no chão."""
    recorte = imagem.subsurface(imagem.get_bounding_rect()).copy()
    w, h = recorte.get_size()
    com_pivo = pygame.Surface((w, h * 2), pygame.SRCALPHA)
    com_pivo.blit(recorte, (0, 0))
    return com_pivo


def _base_do_sprite(imagem):
    """Distância entre o fim da imagem e o fim do desenho (margem transparente embaixo)."""
    return imagem.get_height() - imagem.get_bounding_rect().bottom


class TelaExploracao:
    """Caminhada automática do Exterminador (de costas) pela porta, salão e escada,
    até o primeiro confronto. Enter pula. É o estado S0 da máquina de estados:
    quando `concluida` vira True, o main começa o duelo (evento ENCONTRO_CHEFE)."""

    def __init__(self):
        self.cena = 0
        self.tempo = 0.0          # tempo dentro da cena atual
        self.tempo_andando = 0.0  # tempo total, para o ritmo dos passos não reiniciar a cada cena
        self.concluida = False
        self.fundos = [carregar_imagem(nome, (WIDTH, HEIGHT)) for nome in FUNDOS_EXPLORACAO]
        self.sprite = _sprite_com_pivo_nos_pes(carregar_imagem(JOGADOR_COSTAS_SPRITE))
        self.escuro = pygame.Surface((WIDTH, HEIGHT))
        self.escuro.fill((0, 0, 0))

    def tratar_evento(self, evento):
        if evento.type == pygame.KEYDOWN and (evento.key in ENTER or evento.key == pygame.K_SPACE):
            self.concluida = True  # pula a caminhada

    def atualizar(self, dt):
        if self.concluida:
            return
        self.tempo += dt
        self.tempo_andando += dt
        if self.tempo >= CENAS[self.cena]["duracao"]:
            if self.cena + 1 >= len(CENAS):
                self.concluida = True
            else:
                self.cena += 1
                self.tempo = 0.0

    def desenhar(self, superficie):
        cena = CENAS[self.cena]
        u = min(self.tempo / cena["duracao"], 1.0)
        x0, y0, s0 = cena["ini"]
        x1, y1, s1 = cena["fim"]
        x, y, escala = x0 + (x1 - x0) * u, y0 + (y1 - y0) * u, s0 + (s1 - s0) * u

        # Passos: o corpo balança de lado e "pesa" a cada passo, com os pés parados no chão.
        fase = self.tempo_andando * PASSOS_POR_SEGUNDO * math.pi
        angulo = 3.0 * math.sin(fase)
        escala *= 1.0 + 0.03 * abs(math.sin(fase))
        figura = pygame.transform.rotozoom(self.sprite, angulo, escala)

        superficie.blit(self.fundos[self.cena], (0, 0))
        superficie.blit(figura, figura.get_rect(center=(round(x), round(y))))

        # Escurece no começo e no fim de cada cena (transição entre elas).
        escurecer = max(1 - self.tempo / FADE_TEMPO, 1 - (cena["duracao"] - self.tempo) / FADE_TEMPO, 0)
        if escurecer > 0:
            self.escuro.set_alpha(int(255 * min(escurecer, 1)))
            superficie.blit(self.escuro, (0, 0))


class TelaDuelo:
    """Tela de combate + pergunta de um duelo. Crie depois de pygame.display.set_mode()."""

    def __init__(self, duelo):
        self.duelo = duelo
        self.fase = FASE_PERGUNTA
        self.selecionada = 0
        self.escolhida = None
        self.tempo_feedback = 0.0
        self.concluida = False  # vira True quando o jogador aperta Enter depois da última resposta

        andar = duelo.andar
        self.nome_chefe = CHEFES[andar]["nome"]
        self.fundo = carregar_imagem(FUNDOS_ANDAR.get(andar), (WIDTH, HEIGHT))
        self.jogador = redimensionar_por_altura(carregar_imagem(JOGADOR_SPRITE), 320)
        self.chefe = carregar_imagem(CHEFES_SPRITE.get(andar), TAMANHO_CHEFE)

        self.fonte_enunciado = carregar_fonte(24)
        self.fonte_opcao = carregar_fonte(22)
        self.fonte_pequena = carregar_fonte(20)
        self.fonte_titulo = carregar_fonte(26, negrito=True)

    # --- entrada e tempo ---------------------------------------------------------
    def tratar_evento(self, evento):
        if evento.type != pygame.KEYDOWN:
            return
        if self.fase == FASE_PERGUNTA:
            n = len(self.duelo.pergunta_atual["opcoes"])
            if evento.key == pygame.K_UP:
                self.selecionada = (self.selecionada - 1) % n
            elif evento.key == pygame.K_DOWN:
                self.selecionada = (self.selecionada + 1) % n
            elif pygame.K_1 <= evento.key <= pygame.K_4 and evento.key - pygame.K_1 < n:
                self.selecionada = evento.key - pygame.K_1
            elif evento.key in ENTER:
                self.escolhida = self.selecionada
                self.duelo.responder(self.escolhida)  # o dano é decidido em regras.py
                self.fase = FASE_FEEDBACK
                self.tempo_feedback = 0.0
        elif evento.key in ENTER and self.tempo_feedback >= ESPERA_MINIMA:
            if self.duelo.terminou:
                self.concluida = True
            else:
                self.duelo.proxima_pergunta()
                self.fase = FASE_PERGUNTA
                self.selecionada = 0
                self.escolhida = None

    def atualizar(self, dt):
        if self.fase == FASE_FEEDBACK:
            self.tempo_feedback += dt

    # --- desenho -----------------------------------------------------------------
    def desenhar(self, superficie):
        superficie.blit(self.fundo, (0, 0))
        self._desenhar_personagem(superficie, self.jogador, JOGADOR_X)
        self._desenhar_personagem(superficie, self.chefe, CHEFE_X)
        self._desenhar_coracoes(superficie)
        self._desenhar_painel(superficie)

    def _desenhar_personagem(self, superficie, imagem, x):
        """Pés no chão (CHAO_Y), com uma sombra embaixo para não parecer que flutua."""
        largura = imagem.get_bounding_rect().width
        sombra = pygame.Surface((largura, 36), pygame.SRCALPHA)
        pygame.draw.ellipse(sombra, (0, 0, 0, 110), sombra.get_rect())
        superficie.blit(sombra, sombra.get_rect(center=(x, CHAO_Y - 4)))
        rect = imagem.get_rect(midbottom=(x, CHAO_Y + _base_do_sprite(imagem)))
        superficie.blit(imagem, rect)

    def _desenhar_coracoes(self, superficie):
        # Só os corações que restam aparecem: o coração perdido some.
        espaco = 44
        _texto(superficie, "Exterminador", self.fonte_pequena, COR_TEXTO, (30, 12))
        for i in range(self.duelo.vidas_jogador):
            desenhar_coracao(superficie, (50 + i * espaco, 56), 34, COR_CORACAO)

        _texto(superficie, self.nome_chefe, self.fonte_pequena, COR_TEXTO, (WIDTH - 30, 12), direita=True)
        for i in range(self.duelo.vidas_chefe):
            desenhar_coracao(superficie, (WIDTH - 50 - i * espaco, 56), 34, COR_CORACAO)

    def _piscando_aceso(self):
        """Durante a piscada alterna aceso/apagado; depois fica aceso."""
        if self.tempo_feedback >= FLASH_TEMPO:
            return True
        return int(self.tempo_feedback / FLASH_PERIODO) % 2 == 0

    def _cor_da_opcao(self, i, pergunta):
        """(fundo, borda) da alternativa i, conforme a fase."""
        if self.fase == FASE_PERGUNTA:
            return (COR_SELECIONADA, COR_TEXTO) if i == self.selecionada else (COR_PAINEL, COR_BORDA)
        acertou = self.duelo.ultimo_acertou
        if i == pergunta["correta"]:
            # A certa fica verde. Se o jogador acertou, é ela que pisca.
            if acertou and not self._piscando_aceso():
                return COR_PAINEL, COR_BORDA
            return COR_ACERTO, COR_TEXTO
        if i == self.escolhida:  # errada escolhida: pisca em vermelho
            if not self._piscando_aceso():
                return COR_PAINEL, COR_BORDA
            return COR_ERRO, COR_TEXTO
        return COR_PAINEL, COR_BORDA

    def _desenhar_painel(self, superficie):
        pygame.draw.rect(superficie, COR_PAINEL, PAINEL, border_radius=14)
        pygame.draw.rect(superficie, COR_BORDA, PAINEL, width=4, border_radius=14)
        x = PAINEL.x + PAINEL_MARGEM
        largura = PAINEL.width - 2 * PAINEL_MARGEM

        pergunta = self.duelo.pergunta_atual
        linhas = quebrar_texto(pergunta["enunciado"], self.fonte_enunciado, largura)
        y = _linhas(superficie, linhas, self.fonte_enunciado, COR_TEXTO, x, PAINEL.y + 18, 30, 5) + 16

        for i, opcao in enumerate(pergunta["opcoes"]):
            rect = pygame.Rect(x, y + i * OPCAO_ESPACO, largura, OPCAO_ALTURA)
            fundo, borda = self._cor_da_opcao(i, pergunta)
            pygame.draw.rect(superficie, fundo, rect, border_radius=8)
            pygame.draw.rect(superficie, borda, rect, width=2, border_radius=8)
            _texto(superficie, f"{i + 1}  {opcao}", self.fonte_opcao, COR_TEXTO,
                   (rect.x + 14, rect.centery - self.fonte_opcao.get_height() // 2))
        y += len(pergunta["opcoes"]) * OPCAO_ESPACO + 10

        if self.fase == FASE_FEEDBACK:
            self._desenhar_resultado(superficie, x, y, largura)

    def _desenhar_resultado(self, superficie, x, y, largura):
        duelo = self.duelo
        acertou = duelo.ultimo_acertou
        cor = COR_ACERTO if acertou else COR_ERRO
        titulo = "Acertou! O chefe perdeu 1 coração." if acertou else "Errou! Você perdeu 1 coração."
        _texto(superficie, titulo, self.fonte_titulo, cor, (x, y))
        if not acertou:
            _linhas(superficie, quebrar_texto(duelo.explicacao, self.fonte_pequena, largura),
                    self.fonte_pequena, COR_TEXTO, x, y + 38, 24, 4)

        if duelo.venceu:
            rodape = "Você derrotou o chefe! Enter para continuar"
        elif duelo.game_over:
            rodape = "Fim de jogo. Enter para continuar"
        else:
            rodape = "Enter para continuar"
        if self.tempo_feedback >= ESPERA_MINIMA:
            _texto(superficie, rodape, self.fonte_pequena, COR_TEXTO,
                   (PAINEL.centerx, PAINEL.bottom - 22), centro=True)

class TelaGameOver:
    def __init__(self):
        self.concluida = False
        self.acao = None           
        self.tempo = 0.0
        self.fonte_titulo = pygame.font.Font(None, 140)
        self.fonte = pygame.font.Font(None, 48)
        self.botoes = {
            "tentar_novamente": pygame.Rect(0, 0, 380, 70),
            "menu": pygame.Rect(0, 0, 380, 70),
        }
        self.botoes["tentar_novamente"].center = (640, 420)
        self.botoes["menu"].center = (640, 510)

    def tratar_evento(self, evento):
        if self.tempo < 0.8:        
            return
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            for acao, rect in self.botoes.items():
                if rect.collidepoint(evento.pos):
                    self._escolher(acao)
        elif evento.type == pygame.KEYDOWN:
            if evento.key in (pygame.K_RETURN, pygame.K_r):
                self._escolher("tentar_novamente")
            elif evento.key == pygame.K_ESCAPE:
                self._escolher("menu")

    def _escolher(self, acao):
        self.acao = acao
        self.concluida = True

    def atualizar(self, dt):
        self.tempo += dt

    def desenhar(self, tela):
        alfa = min(255, int(self.tempo / 1.0 * 255))   
        sombra = pygame.Surface(tela.get_size())
        sombra.fill((12, 0, 4))
        sombra.set_alpha(alfa)
        tela.blit(sombra, (0, 0))

        titulo = self.fonte_titulo.render("GAME OVER", True, (200, 30, 40))
        titulo.set_alpha(alfa)
        tela.blit(titulo, titulo.get_rect(center=(640, 250)))

        mouse = pygame.mouse.get_pos()
        nomes = {"tentar_novamente": "TENTAR NOVAMENTE", "menu": "MENU"}
        for acao, rect in self.botoes.items():
            cor = COR_BOTAO_HOVER if rect.collidepoint(mouse) else COR_BOTAO
            pygame.draw.rect(tela, cor, rect, border_radius=10)
            pygame.draw.rect(tela, COR_BORDA, rect, width=4, border_radius=10)
            texto = self.fonte.render(nomes[acao], True, WHITE)
            tela.blit(texto, texto.get_rect(center=rect.center))

