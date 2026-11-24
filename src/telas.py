"""Telas de exploração, pergunta, combate e game over (pygame). Só desenham e leem o teclado:
quem decide o dano é o Duelo, em regras.py."""
import math

import pygame

from config.config import (
    ALTURA_JOGADOR_MEDIA, COR_ACERTO, COR_BORDA, COR_CORACAO, COR_DANO, COR_ERRO, COR_GAME_OVER, COR_OURO,
    COR_PAINEL, COR_SELECIONADA, COR_TEXTO, HEIGHT, WIDTH,
)
from src.recursos import (
    CHEFES_SPRITE, FUNDOS_ANDAR, FUNDOS_EXPLORACAO, JOGADOR_COSTAS_SPRITE, JOGADOR_ESQUERDA_SPRITE, JOGADOR_SPRITE,
    SOM_ACERTO, SOM_ERRO, SOM_GAME_OVER, SOM_PASSOS, SOM_VITORIA,
    alternar_mudo, carregar_fonte, carregar_imagem, redimensionar_por_altura, som_mudo, tocar_som,
)
from src.chefes import CHEFES, CHEFES_INFOS

# Fases do duelo na tela:
#   PERGUNTA  -> o jogador escolhe a alternativa
#   PISCADA   -> a alternativa escolhida pisca (verde se acertou, vermelho se errou)
#   ATAQUE    -> a pergunta sai da tela e o golpe acontece (quem acertou/errou leva dano)
#   RESULTADO -> a pergunta volta, com o resultado e a explicação; Enter continua
FASE_PERGUNTA = "PERGUNTA"
FASE_PISCADA = "PISCADA"
FASE_ATAQUE = "ATAQUE"
FASE_RESULTADO = "RESULTADO"

ENTER = (pygame.K_RETURN, pygame.K_KP_ENTER)

# --- Combate ---
TAMANHO_CHEFE = (288, 336)
ALTURA_JOGADOR = ALTURA_JOGADOR_MEDIA  # altura do Exterminador no combate (o Lobisomem tem ~332 px)
CHEFES_ESPELHADOS = {4}  # chefes cuja arte olha para a direita: viram para encarar o Exterminador
JOGADOR_X = 170
CHEFE_X = 1100
CHAO_Y = 650  # onde os pés dos personagens tocam o chão

PAINEL = pygame.Rect(340, 86, 600, 470)  # pergunta no meio da tela
PAINEL_MARGEM = 20
OPCAO_ALTURA = 40
OPCAO_ESPACO = 46
FLASH_TEMPO = 0.8      # segundos em que a alternativa pisca depois de responder
FLASH_PERIODO = 0.12   # duração de cada "aceso" e "apagado"
ESPERA_MINIMA = 0.3    # na tela de resultado, só dá para continuar depois deste tempo

# Golpe (tudo em segundos, contados desde o início da fase ATAQUE)
PAINEL_TRANSICAO = 0.2   # tempo da pergunta para sair da tela e para voltar
GOLPE_INICIO = 0.2       # o golpe começa quando a pergunta já saiu
GOLPE_DURACAO = 0.85
ATAQUE_TEMPO = GOLPE_INICIO + GOLPE_DURACAO + PAINEL_TRANSICAO
GOLPE_IMPACTO = 0.42     # fração do golpe em que a espada acerta
ANGULO_GOLPE = 28        # inclinação do corpo no golpe, em graus
RECUO_DANO = 22          # quanto quem levou o golpe é empurrado, em pixels
DANO_TEMPO = 0.5         # duração da piscada vermelha de quem levou dano
DANO_PERIODO = 0.08

# --- Exploração ---
# Cada cena é um caminho: o Exterminador começa embaixo (y[0]) e chega ao fim em cima (y[1]).
#   tempo   : segundos para atravessar a cena andando sem parar
#   y       : y dos pés no início e no fim do caminho
#   escala  : tamanho do sprite no início e no fim (encolhe ao se afastar, pela perspectiva)
#   x_ini / x_fim : limites para os lados (min, max) no início e no fim; ficam perto do tapete
CENAS = (
    {"tempo": 3.2, "y": (700, 548), "escala": (0.75, 0.40), "x_ini": (380, 900), "x_fim": (500, 780)},   # porta
    {"tempo": 3.6, "y": (705, 528), "escala": (0.70, 0.30), "x_ini": (380, 900), "x_fim": (540, 740)},   # salão
    {"tempo": 5.5, "y": (710, 378), "escala": (0.70, 0.22), "x_ini": (300, 980), "x_fim": (520, 760)},   # escada
)
# Andares 2 a 4: sobe a escada e depois anda pelo corredor até a porta do chefe.
CENA_ESCADA = {"tempo": 4.5, "y": (700, 412), "escala": (0.75, 0.34), "x_ini": (250, 1030), "x_fim": (520, 760)}
CENA_CORREDOR = {"tempo": 4.5, "y": (700, 412), "escala": (0.75, 0.34), "x_ini": (250, 1030), "x_fim": (520, 760)}
CENAS_POR_ANDAR = {
    1: CENAS,
    2: (CENA_ESCADA, CENA_CORREDOR),
    3: (CENA_ESCADA, CENA_CORREDOR),
    4: (CENA_ESCADA, CENA_CORREDOR),
}
X_INICIAL = 640
VELOCIDADE_LATERAL = 170     # px/s para os lados, no tamanho inicial (diminui ao se afastar)
ALTURA_REF_EXPLORADOR = 276  # altura (px) do desenho do Exterminador quando a escala da cena é 1.0
ESCALA_EXPLORADOR = 0.9      # multiplica todas as escalas das cenas (diminua para ficar menor)
FADE_TEMPO = 0.4
PASSOS_POR_SEGUNDO = 3.2  # cada passo = um balanço do corpo

# --- Andar concluído (estrelas) ---
ANDAR_CONCLUIDO_ESPERA = 0.5            # tempo até aceitar teclas, para não pular sem querer
PAINEL_ESTRELAS = pygame.Rect(340, 100, 600, 520)
ROTULOS_ACAO = {"repetir": "Tentar de novo para ganhar mais estrelas", "continuar": "Continuar"}

# --- Baú da exploração ---
BAU_CENA = 1                  # índice da cena (o corredor) em que o baú fica
BAU_POS = (790, 565)          # onde o baú encosta no chão
BAU_LARGURA = 72
BAU_ALCANCE = (160, 70)       # distância (x, y) para aparecer o botão ABRIR
BOTAO_ABRIR = pygame.Rect(0, 0, 150, 44)
BAU_MENSAGEM_TEMPO = 3.0
PAINEL_BAU = pygame.Rect(340, 70, 600, 540)
BAU_ESPERA = 0.3              # na tela do resultado, só dá para fechar depois deste tempo

# --- Dicas na tela e pausa ---
DICA_EXPLORACAO = "W A S D ou setas: andar   ·   Enter: ir direto ao chefe   ·   ESC: pausa"
DICA_DUELO = "↑ ↓ ou 1 a 4: escolher   ·   Enter ou clique: responder   ·   ESC: pausa"
DICA_CONFIRMAR = "← →: escolher   ·   Enter: aplicar   ·   Backspace: voltar às alternativas"
ROTULOS_CONFIRMAR = ("Confirmar", "Cancelar")
DICA_TEMPO = 7.0           # a dica da exploração fica este tempo e some devagar
DICA_FADE = 1.0
PAINEL_PAUSA = pygame.Rect(440, 170, 400, 380)
ACOES_PAUSA = ("continuar", "som", "menu", "sair")

# --- Game Over ---
GAME_OVER_ATRASO = 2.0  # a mensagem para recomeçar aparece depois deste tempo


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


def desenhar_estrela(superficie, centro, raio, preenchida):
    """Estrela de 5 pontas: dourada se ganhou, só o contorno apagado se não ganhou."""
    cx, cy = centro
    pontos = []
    for i in range(10):
        angulo = -math.pi / 2 + i * math.pi / 5
        r = raio if i % 2 == 0 else raio * 0.42
        pontos.append((cx + r * math.cos(angulo), cy + r * math.sin(angulo)))
    if preenchida:
        pygame.draw.polygon(superficie, COR_OURO, pontos)
        pygame.draw.polygon(superficie, COR_BORDA, pontos, 3)
    else:
        pygame.draw.polygon(superficie, (70, 62, 90), pontos)
        pygame.draw.polygon(superficie, (120, 110, 140), pontos, 3)


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


def desenhar_dica(superficie, texto, centro, opacidade=255, tamanho=20):
    """Faixa escura com uma linha de texto (instruções de controle). `opacidade` de 0 a 255."""
    fonte = carregar_fonte(tamanho)
    imagem = fonte.render(texto, True, COR_TEXTO)
    faixa = pygame.Surface((imagem.get_width() + 40, imagem.get_height() + 14), pygame.SRCALPHA)
    pygame.draw.rect(faixa, (10, 8, 18, 190), faixa.get_rect(), border_radius=10)
    faixa.blit(imagem, (20, 7))
    faixa.set_alpha(opacidade)
    superficie.blit(faixa, faixa.get_rect(center=centro))


def desenhar_bau(superficie, base, largura, aberto=False):
    """Baú desenhado em código (sem arquivo de imagem). `base` é o ponto central onde ele toca o chão."""
    contorno = (20, 16, 28)
    altura = int(largura * 0.55)
    corpo = pygame.Rect(0, 0, largura, altura)
    corpo.midbottom = base
    sombra = pygame.Surface((largura + 30, 26), pygame.SRCALPHA)
    pygame.draw.ellipse(sombra, (0, 0, 0, 110), sombra.get_rect())
    superficie.blit(sombra, sombra.get_rect(center=(base[0], base[1] - 2)))

    pygame.draw.rect(superficie, (126, 78, 38), corpo, border_radius=6)
    pygame.draw.rect(superficie, (86, 52, 26), (corpo.x, corpo.y + altura // 2, largura, altura // 2), border_radius=6)
    if aberto:   # tampa levantada e luz dourada de dentro
        brilho = pygame.Surface((largura, altura), pygame.SRCALPHA)
        pygame.draw.ellipse(brilho, (255, 214, 102, 150), brilho.get_rect())
        superficie.blit(brilho, brilho.get_rect(midbottom=(base[0], corpo.y + 10)))
        tampa = pygame.Rect(0, 0, largura, int(altura * 0.55))
        tampa.midbottom = (base[0], corpo.y - int(altura * 0.35))
        pygame.draw.rect(superficie, (150, 94, 46), tampa, border_radius=6)
        pygame.draw.rect(superficie, contorno, tampa, width=3, border_radius=6)
    else:
        tampa = pygame.Rect(corpo.x, corpo.y - int(altura * 0.28), largura, int(altura * 0.5))
        pygame.draw.rect(superficie, (150, 94, 46), tampa, border_radius=10)
        pygame.draw.rect(superficie, contorno, tampa, width=3, border_radius=10)
        pygame.draw.rect(superficie, COR_OURO, (corpo.centerx - 9, corpo.y - 4, 18, 22), border_radius=3)
        pygame.draw.rect(superficie, contorno, (corpo.centerx - 9, corpo.y - 4, 18, 22), width=2, border_radius=3)
    topo_tiras = corpo.y if aberto else tampa.y + 2
    for x in (corpo.x + largura // 5, corpo.right - largura // 5 - 8):   # tiras de metal
        pygame.draw.rect(superficie, COR_OURO, (x, topo_tiras, 8, corpo.bottom - topo_tiras))
    pygame.draw.rect(superficie, contorno, corpo, width=3, border_radius=6)


def _botoes_de_confirmacao(topo, centro_x, altura_fonte):
    """Retângulos de Confirmar e Cancelar: lado a lado, centralizados, abaixo do texto que começa em `topo`."""
    y = topo + altura_fonte + 12
    largura, espaco = 230, 30
    esquerda = centro_x - largura - espaco // 2
    return [pygame.Rect(esquerda, y, largura, 46), pygame.Rect(esquerda + largura + espaco, y, largura, 46)]


def _desenhar_confirmacao_comum(superficie, texto, fonte_titulo, fonte_botao, topo, centro_x, foco):
    """'Confirmar a resposta N?' em letra grande, na linha toda, e os botões Confirmar e Cancelar embaixo."""
    _texto(superficie, texto, fonte_titulo, COR_TEXTO, (centro_x, topo + fonte_titulo.get_height() // 2), centro=True)
    for i, (rotulo, rect) in enumerate(zip(ROTULOS_CONFIRMAR, _botoes_de_confirmacao(topo, centro_x, fonte_titulo.get_height()))):
        ativo = i == foco
        pygame.draw.rect(superficie, COR_SELECIONADA if ativo else COR_PAINEL, rect, border_radius=8)
        pygame.draw.rect(superficie, COR_TEXTO if ativo else COR_BORDA, rect, width=2, border_radius=8)
        _texto(superficie, rotulo, fonte_botao, COR_TEXTO, rect.center, centro=True)


def _sprite_com_pivo_nos_pes(imagem, altura=None):
    """Recorta as margens transparentes e devolve uma superfície com o centro nos pés.
    Assim, girar e escalar (rotozoom) mantém os pés parados no chão.
    Se `altura` for dada, o desenho é redimensionado para ela antes (independe do tamanho do arquivo)."""
    recorte = imagem.subsurface(imagem.get_bounding_rect()).copy()
    if altura is not None:
        recorte = redimensionar_por_altura(recorte, altura)
    w, h = recorte.get_size()
    com_pivo = pygame.Surface((w, h * 2), pygame.SRCALPHA)
    com_pivo.blit(recorte, (0, 0))
    return com_pivo


def _base_do_sprite(imagem):
    """Distância entre o fim da imagem e o fim do desenho (margem transparente embaixo)."""
    return imagem.get_height() - imagem.get_bounding_rect().bottom


def _suave(u):
    """Transição suave de 0 a 1 (começa e termina devagar)."""
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)


def curva_golpe(u):
    """Movimento de um golpe, para u de 0 (início) a 1 (fim). Devolve (avanço, inclinação):
    - avanço: 0 na posição de origem e 1 junto do alvo (ida rápida, volta suave);
    - inclinação: negativa = corpo para trás (preparo), 1 = corpo inclinado no golpe, 0 = em pé."""
    u = max(0.0, min(1.0, u))
    if u < 0.40:
        avanco = _suave(u / 0.40)
    elif u < 0.55:
        avanco = 1.0
    else:
        avanco = 1.0 - _suave((u - 0.55) / 0.45)

    if u < 0.15:
        inclinacao = -0.4 * _suave(u / 0.15)
    elif u < 0.40:
        inclinacao = -0.4 + 1.4 * _suave((u - 0.15) / 0.25)
    elif u < 0.55:
        inclinacao = 1.0
    else:
        inclinacao = 1.0 - _suave((u - 0.55) / 0.35)
    return avanco, inclinacao


class TelaExploracao:
    """O jogador anda com o Exterminador (de costas) pela porta, salão e escada, com W, A, S, D
    ou as setas, até o primeiro confronto. É o estado S0 da máquina de estados.

    W/↑ avança (sobe na tela e ele encolhe pela perspectiva), S/↓ volta, A/D e ←/→ andam de lado,
    sem sair do caminho. Chegar ao fim de uma cena leva à próxima; no topo da escada a tela
    fica `concluida` e o main começa o duelo (evento ENCONTRO_CHEFE). Enter ou Espaço pulam."""

    def __init__(self, andar=1, com_bau=False):
        self.andar = andar
        self.cenas = CENAS_POR_ANDAR[andar]
        self.com_bau = com_bau        # há um baú fechado no corredor deste andar?
        self.bau_aberto = False
        self.pedir_bau = False        # vira True quando o jogador clica em ABRIR; o main mostra a pergunta
        self.mensagem_bau = None      # (texto, tempo restante) depois de abrir o baú
        self.fonte_botao = carregar_fonte(24, negrito=True)
        self.fonte_dica = carregar_fonte(16)
        self.tempo_andando = 0.0  # só conta enquanto anda, para o ritmo dos passos
        self.andando = False
        self.tempo_cena = 0.0      # para a dica de controles aparecer no começo e sumir
        self.passos_dados = 0     # escolhe qual variação do som de passo toca
        self.concluida = False
        self.fundos = [carregar_imagem(nome, (WIDTH, HEIGHT)) for nome in FUNDOS_EXPLORACAO[andar]]
        self.sprite = _sprite_com_pivo_nos_pes(carregar_imagem(JOGADOR_COSTAS_SPRITE), ALTURA_REF_EXPLORADOR)
        esquerda = _sprite_com_pivo_nos_pes(carregar_imagem(JOGADOR_ESQUERDA_SPRITE), ALTURA_REF_EXPLORADOR)
        self.sprites = {
            "cima":     self.sprite,
            "baixo":    _sprite_com_pivo_nos_pes(carregar_imagem(JOGADOR_SPRITE), ALTURA_REF_EXPLORADOR),
            "esquerda": esquerda,
            "direita":  pygame.transform.flip(esquerda, True, False),
        }
        self.direcao = "cima"
        self.escuro = pygame.Surface((WIDTH, HEIGHT))
        self.escuro.fill((0, 0, 0))
        self._iniciar_cena(0)

    def _iniciar_cena(self, indice):
        self.cena = indice
        self.y = float(self.cenas[indice]["y"][0])
        self.x = float(self._limitar_x(X_INICIAL, self.y))
        self.fade_entrada = FADE_TEMPO   # escurece no começo da cena
        self.fade_saida = None           # vira um tempo quando o jogador chega ao fim da cena

    def _progresso(self):
        """0 no início do caminho e 1 no fim."""
        y0, y1 = self.cenas[self.cena]["y"]
        return max(0.0, min(1.0, (y0 - self.y) / (y0 - y1)))

    def _escala_bruta(self):
        s0, s1 = self.cenas[self.cena]["escala"]
        return s0 + (s1 - s0) * self._progresso()

    def _limitar_x(self, x, y=None):
        """Mantém o x dentro do caminho, que estreita conforme ele se afasta."""
        cena = self.cenas[self.cena]
        y = self.y if y is None else y
        y0, y1 = cena["y"]
        u = max(0.0, min(1.0, (y0 - y) / (y0 - y1)))
        minimo = cena["x_ini"][0] + (cena["x_fim"][0] - cena["x_ini"][0]) * u
        maximo = cena["x_ini"][1] + (cena["x_fim"][1] - cena["x_ini"][1]) * u
        return max(minimo, min(maximo, x))

    @property
    def perto_do_bau(self):
        """Baú fechado neste andar e o Exterminador está perto dele (na cena do baú)?"""
        return (self.com_bau and not self.bau_aberto and self.cena == BAU_CENA and self.fade_saida is None
                and abs(self.x - BAU_POS[0]) <= BAU_ALCANCE[0] and abs(self.y - BAU_POS[1]) <= BAU_ALCANCE[1])

    def _botao_abrir(self):
        botao = BOTAO_ABRIR.copy()
        botao.midbottom = (BAU_POS[0], BAU_POS[1] - int(BAU_LARGURA * 0.55) - 36)
        return botao

    def bau_resolvido(self, ganhou):
        """O main chama depois da pergunta do baú: o baú fica aberto e aparece o resultado."""
        self.bau_aberto = True
        self.pedir_bau = False
        texto = "+1 coração! Você ganhou uma vida extra." if ganhou else "O baú estava vazio..."
        self.mensagem_bau = [texto, BAU_MENSAGEM_TEMPO, ganhou]

    def tratar_evento(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.perto_do_bau and self._botao_abrir().collidepoint(evento.pos):
                self.pedir_bau = True
        elif evento.type == pygame.KEYDOWN:
            if evento.key in ENTER and self.perto_do_bau:
                self.pedir_bau = True      # perto do baú, Enter abre (e não pula a exploração)
            elif evento.key in ENTER or evento.key == pygame.K_SPACE:
                self.concluida = True  # pula a exploração

    def atualizar(self, dt, teclas=None):
        """`teclas` é o estado do teclado (pygame.key.get_pressed()); os testes passam o seu."""
        if self.concluida:
            return
        self.tempo_cena += dt
        if self.mensagem_bau is not None:
            self.mensagem_bau[1] -= dt
            if self.mensagem_bau[1] <= 0:
                self.mensagem_bau = None
        if self.fade_saida is not None:  # chegou ao fim da cena: escurece e troca
            self.fade_saida += dt
            if self.fade_saida >= FADE_TEMPO:
                if self.cena + 1 >= len(self.cenas):
                    self.concluida = True
                else:
                    self._iniciar_cena(self.cena + 1)
            return
        self.fade_entrada = max(0.0, self.fade_entrada - dt)

        if teclas is None:
            teclas = pygame.key.get_pressed()
        direita = bool(teclas[pygame.K_d] or teclas[pygame.K_RIGHT])
        esquerda = bool(teclas[pygame.K_a] or teclas[pygame.K_LEFT])
        baixo = bool(teclas[pygame.K_s] or teclas[pygame.K_DOWN])
        cima = bool(teclas[pygame.K_w] or teclas[pygame.K_UP])
        dx, dy = direita - esquerda, baixo - cima
        if dx and dy:  # na diagonal não anda mais rápido
            dx, dy = dx * math.sqrt(0.5), dy * math.sqrt(0.5)
        # vira o boneco conforme a tecla; parado, mantém a última direção
        if dx > 0:
            self.direcao = "direita"
        elif dx < 0:
            self.direcao = "esquerda"
        elif dy > 0:
            self.direcao = "baixo"
        elif dy < 0:
            self.direcao = "cima"

        cena = self.cenas[self.cena]
        y_ini, y_fim = cena["y"]
        velocidade_frente = (y_ini - y_fim) / cena["tempo"]
        velocidade_lado = VELOCIDADE_LATERAL * self._escala_bruta() / cena["escala"][0]  # mais devagar ao longe
        self.y = max(float(y_fim), min(float(y_ini), self.y + dy * velocidade_frente * dt))
        self.x = self._limitar_x(self.x + dx * velocidade_lado * dt)

        andava = self.andando
        self.andando = bool(dx or dy)
        if self.andando:
            passos_antes = int(self.tempo_andando * PASSOS_POR_SEGUNDO)
            self.tempo_andando += dt
            # um som de passo a cada passo do balanço do desenho (o primeiro toca ao começar a andar)
            if not andava or int(self.tempo_andando * PASSOS_POR_SEGUNDO) > passos_antes:
                tocar_som(SOM_PASSOS[self.passos_dados % len(SOM_PASSOS)])
                self.passos_dados += 1
        if self.y <= y_fim:
            self.fade_saida = 0.0

    def desenhar(self, superficie):
        escala = self._escala_bruta() * ESCALA_EXPLORADOR
        angulo = 0.0
        if self.andando:  # passos: o corpo balança de lado e "pesa", com os pés parados no chão
            fase = self.tempo_andando * PASSOS_POR_SEGUNDO * math.pi
            angulo = 3.0 * math.sin(fase)
            escala *= 1.0 + 0.03 * abs(math.sin(fase))
        figura = pygame.transform.rotozoom(self.sprites[self.direcao], angulo, escala)

        superficie.blit(self.fundos[self.cena], (0, 0))
        mostra_bau = self.com_bau and self.cena == BAU_CENA
        if mostra_bau and self.y <= BAU_POS[1]:      # o Exterminador está mais ao fundo: o baú fica na frente
            desenhar_bau(superficie, BAU_POS, BAU_LARGURA, self.bau_aberto)
        superficie.blit(figura, figura.get_rect(center=(round(self.x), round(self.y))))
        if mostra_bau and self.y > BAU_POS[1]:
            desenhar_bau(superficie, BAU_POS, BAU_LARGURA, self.bau_aberto)
        if self.perto_do_bau:                        # botão ABRIR (Enter ou clique)
            botao = self._botao_abrir()
            pygame.draw.rect(superficie, COR_SELECIONADA, botao, border_radius=10)
            pygame.draw.rect(superficie, COR_OURO, botao, width=3, border_radius=10)
            _texto(superficie, "ABRIR", self.fonte_botao, COR_TEXTO, botao.center, centro=True)
            _texto(superficie, "Enter ou clique", self.fonte_dica, COR_TEXTO, (botao.centerx, botao.bottom + 14), centro=True)
        if self.mensagem_bau is not None:
            texto, restante, ganhou = self.mensagem_bau
            faixa = pygame.Surface((560, 56), pygame.SRCALPHA)
            pygame.draw.rect(faixa, (10, 8, 18, 220), faixa.get_rect(), border_radius=12)
            pygame.draw.rect(faixa, COR_OURO if ganhou else COR_ERRO, faixa.get_rect(), width=3, border_radius=12)
            superficie.blit(faixa, faixa.get_rect(center=(WIDTH // 2, 90)))
            _texto(superficie, texto, self.fonte_botao, COR_OURO if ganhou else COR_TEXTO, (WIDTH // 2, 90), centro=True)

        if self.cena == 0 and self.tempo_cena < DICA_TEMPO + DICA_FADE:   # dica de controles ao entrar no andar
            opacidade = 255 * min(1.0, (DICA_TEMPO + DICA_FADE - self.tempo_cena) / DICA_FADE)
            desenhar_dica(superficie, DICA_EXPLORACAO, (WIDTH // 2, HEIGHT - 40), int(opacidade))

        # Escurece no começo da cena e ao chegar no fim (transição entre cenas).
        escurecer = self.fade_entrada / FADE_TEMPO
        if self.fade_saida is not None:
            escurecer = max(escurecer, self.fade_saida / FADE_TEMPO)
        if escurecer > 0:
            self.escuro.set_alpha(int(255 * min(escurecer, 1)))
            superficie.blit(self.escuro, (0, 0))


class TelaDuelo:
    """Tela de combate + pergunta de um duelo. Crie depois de pygame.display.set_mode().

    Depois que o jogador responde: a alternativa pisca (PISCADA), a pergunta sai da tela e o
    personagem que acertou ou errou aplica o golpe (ATAQUE), e a pergunta volta com o resultado
    (RESULTADO). O dano em si já foi decidido em regras.py; aqui só se mostra."""

    def __init__(self, duelo):
        self.duelo = duelo
        self.fase = FASE_PERGUNTA
        self.tempo_fase = 0.0
        self.selecionada = 0
        self.escolhida = None
        self.confirmando = False   # True: perguntando "Confirmar a resposta?" antes de valer
        self.foco_confirmar = 0    # 0 = Confirmar, 1 = Cancelar
        self.concluida = False  # vira True quando o jogador aperta Enter depois da última resposta

        # Corações mostrados na tela: só mudam no momento do golpe, não quando se responde.
        self.vidas_jogador_ex = duelo.vidas_jogador
        self.vidas_chefe_ex = duelo.vidas_chefe

        andar = duelo.andar
        self.nome_chefe = CHEFES[andar]["nome"]
        self.fundo = carregar_imagem(FUNDOS_ANDAR.get(andar), (WIDTH, HEIGHT))
        self.jogador = redimensionar_por_altura(carregar_imagem(JOGADOR_SPRITE), ALTURA_JOGADOR)
        self.chefe = carregar_imagem(CHEFES_SPRITE.get(andar), TAMANHO_CHEFE)
        if andar in CHEFES_ESPELHADOS:
            self.chefe = pygame.transform.flip(self.chefe, True, False)  # espelha na horizontal

        # Versões com o pivô nos pés (para inclinar o corpo no golpe) e centro do desenho.
        self._pivo_jogador = _sprite_com_pivo_nos_pes(self.jogador)
        self._pivo_chefe = _sprite_com_pivo_nos_pes(self.chefe)
        bbox_j, bbox_c = self.jogador.get_bounding_rect(), self.chefe.get_bounding_rect()
        self._desvio_jogador = bbox_j.centerx - self.jogador.get_width() / 2
        self._desvio_chefe = bbox_c.centerx - self.chefe.get_width() / 2
        # Quanto quem ataca avança: até ficar perto do outro.
        self.distancia_golpe = (CHEFE_X - JOGADOR_X) - (bbox_j.width + bbox_c.width) / 2 - 30

        self.buffer_painel = pygame.Surface(PAINEL.size, pygame.SRCALPHA)
        self.fonte_enunciado = carregar_fonte(24)
        self.fonte_opcao = carregar_fonte(22)
        self.fonte_pequena = carregar_fonte(20)
        self.fonte_dica = carregar_fonte(16)
        self.fonte_titulo = carregar_fonte(26, negrito=True)

    def _ir_para(self, fase):
        self.fase = fase
        self.tempo_fase = 0.0

    def _sincronizar_coracoes(self):
        self.vidas_jogador_ex = self.duelo.vidas_jogador
        self.vidas_chefe_ex = self.duelo.vidas_chefe

    # --- entrada e tempo ---------------------------------------------------------
    def _confirmar(self):
        """Confirma a alternativa selecionada. O dano é decidido em regras.py."""
        self.escolhida = self.selecionada
        acertou = self.duelo.responder(self.escolhida)
        tocar_som(SOM_ACERTO if acertou else SOM_ERRO)
        self._ir_para(FASE_PISCADA)

    def _perguntar_confirmacao(self):
        """Enter ou clique numa alternativa: antes de valer, pergunta 'Confirmar a resposta?'."""
        self.confirmando = True
        self.foco_confirmar = 0

    def _aplicar_confirmacao(self):
        if self.foco_confirmar == 0:
            self.confirmando = False
            self._confirmar()
        else:                      # Cancelar: volta a escolher a alternativa
            self.confirmando = False

    def _botoes_confirmacao(self, pergunta):
        """Retângulos de Confirmar e Cancelar, relativos ao painel: centralizados, abaixo da pergunta de confirmação."""
        topo = self._retangulos_opcoes(pergunta)[-1].bottom + 16
        return _botoes_de_confirmacao(topo, PAINEL.width // 2, self.fonte_titulo.get_height())

    def _botao_sob(self, pos):
        for i, rect in enumerate(self._botoes_confirmacao(self.duelo.pergunta_atual)):
            if rect.move(PAINEL.x, PAINEL.y).collidepoint(pos):
                return i
        return None

    def _continuar(self):
        """Na tela de resultado: segue para a próxima pergunta ou encerra o duelo."""
        if self.tempo_fase < ESPERA_MINIMA:
            return
        if self.duelo.terminou:
            self.concluida = True
        else:
            self.duelo.proxima_pergunta()
            self.selecionada = 0
            self.escolhida = None
            self._ir_para(FASE_PERGUNTA)

    def _opcao_sob(self, pos):
        """Índice da alternativa que está sob o mouse (ou None)."""
        for i, rect in enumerate(self._retangulos_opcoes(self.duelo.pergunta_atual)):
            if rect.move(PAINEL.x, PAINEL.y).collidepoint(pos):
                return i
        return None

    def tratar_evento(self, evento):
        # Mouse (além do teclado): passar por cima seleciona, clicar escolhe e confirma.
        if evento.type == pygame.MOUSEMOTION and self.fase == FASE_PERGUNTA:
            if self.confirmando:
                b = self._botao_sob(evento.pos)
                if b is not None:
                    self.foco_confirmar = b
            else:
                i = self._opcao_sob(evento.pos)
                if i is not None:
                    self.selecionada = i
            return
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.fase == FASE_PERGUNTA and self.confirmando:
                b = self._botao_sob(evento.pos)
                if b is not None:
                    self.foco_confirmar = b
                    self._aplicar_confirmacao()
            elif self.fase == FASE_PERGUNTA:
                i = self._opcao_sob(evento.pos)
                if i is not None:
                    self.selecionada = i
                    self._perguntar_confirmacao()
            elif self.fase == FASE_RESULTADO:
                self._continuar()
            return

        if evento.type != pygame.KEYDOWN:
            return
        if self.fase == FASE_PERGUNTA and self.confirmando:
            if evento.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN):
                self.foco_confirmar = 1 - self.foco_confirmar
            elif evento.key in ENTER:
                self._aplicar_confirmacao()
            elif evento.key == pygame.K_BACKSPACE:
                self.confirmando = False
            elif pygame.K_1 <= evento.key <= pygame.K_4 and evento.key - pygame.K_1 < len(self.duelo.pergunta_atual["opcoes"]):
                self.selecionada = evento.key - pygame.K_1   # escolher outra alternativa desfaz a pergunta
                self.confirmando = False
        elif self.fase == FASE_PERGUNTA:
            n = len(self.duelo.pergunta_atual["opcoes"])
            if evento.key == pygame.K_UP:
                self.selecionada = (self.selecionada - 1) % n
            elif evento.key == pygame.K_DOWN:
                self.selecionada = (self.selecionada + 1) % n
            elif pygame.K_1 <= evento.key <= pygame.K_4 and evento.key - pygame.K_1 < n:
                self.selecionada = evento.key - pygame.K_1
            elif evento.key in ENTER:
                self._perguntar_confirmacao()
        elif self.fase == FASE_RESULTADO and evento.key in ENTER:
            self._continuar()

    def atualizar(self, dt):
        self.tempo_fase += dt
        if self.fase == FASE_PISCADA and self.tempo_fase >= FLASH_TEMPO:
            self._ir_para(FASE_ATAQUE)
        elif self.fase == FASE_ATAQUE:
            if self._tempo_depois_do_impacto() >= 0:
                self._sincronizar_coracoes()  # o coração some no momento do golpe
            if self.tempo_fase >= ATAQUE_TEMPO:
                self._sincronizar_coracoes()
                self._ir_para(FASE_RESULTADO)

    # --- golpe -------------------------------------------------------------------
    def _progresso_golpe(self):
        """De 0 a 1 ao longo do golpe (0 antes de começar)."""
        return max(0.0, min(1.0, (self.tempo_fase - GOLPE_INICIO) / GOLPE_DURACAO))

    def _tempo_depois_do_impacto(self):
        """Segundos desde que a espada (ou a garra) acertou; negativo antes do impacto."""
        return self.tempo_fase - GOLPE_INICIO - GOLPE_IMPACTO * GOLPE_DURACAO

    def _poses(self):
        """Devolve ((dx, ângulo, piscando) do Exterminador, (dx, ângulo, piscando) do chefe)."""
        parado = (0.0, 0.0, False)
        if self.fase != FASE_ATAQUE:
            return parado, parado
        jogador_ataca = bool(self.duelo.ultimo_acertou)
        sentido = 1 if jogador_ataca else -1  # o Exterminador avança para a direita; o chefe, para a esquerda
        avanco, inclinacao = curva_golpe(self._progresso_golpe())
        atacante = (sentido * self.distancia_golpe * avanco, -sentido * inclinacao * ANGULO_GOLPE, False)

        depois = self._tempo_depois_do_impacto()
        alvo = parado
        if 0 <= depois < DANO_TEMPO:
            recuo = sentido * RECUO_DANO * math.sin(math.pi * depois / DANO_TEMPO)
            alvo = (recuo, 0.0, int(depois / DANO_PERIODO) % 2 == 0)
        return (atacante, alvo) if jogador_ataca else (alvo, atacante)

    # --- desenho -----------------------------------------------------------------
    def desenhar(self, superficie):
        superficie.blit(self.fundo, (0, 0))
        pose_jogador, pose_chefe = self._poses()
        self._desenhar_personagem(superficie, self.jogador, self._pivo_jogador, self._desvio_jogador,
                                  JOGADOR_X, *pose_jogador)
        self._desenhar_personagem(superficie, self.chefe, self._pivo_chefe, self._desvio_chefe,
                                  CHEFE_X, *pose_chefe)
        self._desenhar_coracoes(superficie)
        self._desenhar_painel(superficie)

    def _desenhar_personagem(self, superficie, imagem, pivo, desvio, x, dx=0.0, angulo=0.0, piscando=False):
        """Pés no chão (CHAO_Y), com uma sombra embaixo para não parecer que flutua.
        `dx` desloca, `angulo` inclina o corpo (em torno dos pés) e `piscando` pinta de vermelho."""
        largura = imagem.get_bounding_rect().width
        sombra = pygame.Surface((largura, 36), pygame.SRCALPHA)
        pygame.draw.ellipse(sombra, (0, 0, 0, 110), sombra.get_rect())
        superficie.blit(sombra, sombra.get_rect(center=(x + dx, CHAO_Y - 4)))

        if dx == 0 and angulo == 0 and not piscando:
            superficie.blit(imagem, imagem.get_rect(midbottom=(x, CHAO_Y + _base_do_sprite(imagem))))
            return
        figura = pygame.transform.rotozoom(pivo, angulo, 1.0)
        if piscando:  # piscada vermelha de quem levou dano (soma vermelho sem mexer na transparência)
            figura = figura.copy()
            figura.fill(COR_DANO, special_flags=pygame.BLEND_RGB_ADD)
        superficie.blit(figura, figura.get_rect(center=(round(x + desvio + dx), CHAO_Y)))

    def _desenhar_coracoes(self, superficie):
        # Só os corações que restam aparecem: o coração perdido some.
        espaco = 44
        _texto(superficie, "Exterminador", self.fonte_pequena, COR_TEXTO, (30, 12))
        for i in range(self.vidas_jogador_ex):
            desenhar_coracao(superficie, (50 + i * espaco, 56), 34, COR_CORACAO)

        _texto(superficie, self.nome_chefe, self.fonte_pequena, COR_TEXTO, (WIDTH - 30, 12), direita=True)
        for i in range(self.vidas_chefe_ex):
            desenhar_coracao(superficie, (WIDTH - 50 - i * espaco, 56), 34, COR_CORACAO)

    def _piscando_aceso(self):
        """Durante a piscada alterna aceso/apagado; depois fica aceso."""
        if self.fase != FASE_PISCADA:
            return True
        return int(self.tempo_fase / FLASH_PERIODO) % 2 == 0

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

    def _retangulos_opcoes(self, pergunta):
        """Retângulos das alternativas, relativos ao painel. O mesmo cálculo serve para desenhar e para o mouse."""
        largura = PAINEL.width - 2 * PAINEL_MARGEM
        linhas = quebrar_texto(pergunta["enunciado"], self.fonte_enunciado, largura)
        topo = 18 + min(len(linhas), 5) * 30 + 16
        return [pygame.Rect(PAINEL_MARGEM, topo + i * OPCAO_ESPACO, largura, OPCAO_ALTURA)
                for i in range(len(pergunta["opcoes"]))]

    def _deslocamento_painel(self):
        """Quanto o painel está deslocado para cima: 0 = no lugar; negativo = saindo da tela."""
        if self.fase != FASE_ATAQUE:
            return 0.0
        distancia = PAINEL.bottom + 10
        t = self.tempo_fase
        if t < PAINEL_TRANSICAO:
            return -distancia * _suave(t / PAINEL_TRANSICAO)
        if t > ATAQUE_TEMPO - PAINEL_TRANSICAO:
            return -distancia * (1 - _suave((t - (ATAQUE_TEMPO - PAINEL_TRANSICAO)) / PAINEL_TRANSICAO))
        return -distancia

    def _desenhar_painel(self, superficie):
        deslocamento = self._deslocamento_painel()
        if deslocamento <= -(PAINEL.bottom + 10):
            return  # a pergunta está fora da tela durante o golpe

        buf = self.buffer_painel
        buf.fill((0, 0, 0, 0))
        area = buf.get_rect()
        pygame.draw.rect(buf, COR_PAINEL, area, border_radius=14)
        pygame.draw.rect(buf, COR_BORDA, area, width=4, border_radius=14)
        x = PAINEL_MARGEM
        largura = PAINEL.width - 2 * PAINEL_MARGEM

        pergunta = self.duelo.pergunta_atual
        linhas = quebrar_texto(pergunta["enunciado"], self.fonte_enunciado, largura)
        _linhas(buf, linhas, self.fonte_enunciado, COR_TEXTO, x, 18, 30, 5)

        retangulos = self._retangulos_opcoes(pergunta)
        for i, (opcao, rect) in enumerate(zip(pergunta["opcoes"], retangulos)):
            fundo, borda = self._cor_da_opcao(i, pergunta)
            pygame.draw.rect(buf, fundo, rect, border_radius=8)
            pygame.draw.rect(buf, borda, rect, width=2, border_radius=8)
            _texto(buf, f"{i + 1}  {opcao}", self.fonte_opcao, COR_TEXTO,
                   (rect.x + 14, rect.centery - self.fonte_opcao.get_height() // 2))
        y = retangulos[-1].y + OPCAO_ESPACO + 10

        if self.fase == FASE_RESULTADO:
            self._desenhar_resultado(buf, x, y, largura)
        elif self.fase == FASE_PERGUNTA:
            if self.confirmando:
                self._desenhar_confirmacao(buf, pergunta)
            _texto(buf, DICA_CONFIRMAR if self.confirmando else DICA_DUELO, self.fonte_dica, (170, 160, 190),
                   (PAINEL.width // 2, PAINEL.height - 22), centro=True)
        superficie.blit(buf, (PAINEL.x, PAINEL.y + round(deslocamento)))

    def _desenhar_confirmacao(self, buf, pergunta):
        """A pergunta 'Confirmar a resposta N?' e os botões Confirmar e Cancelar, abaixo das alternativas."""
        topo = self._retangulos_opcoes(pergunta)[-1].bottom + 16
        _desenhar_confirmacao_comum(buf, f"Confirmar a resposta {self.selecionada + 1}?", self.fonte_titulo,
                                    self.fonte_opcao, topo, PAINEL.width // 2, self.foco_confirmar)

    def _desenhar_resultado(self, buf, x, y, largura):
        duelo = self.duelo
        acertou = duelo.ultimo_acertou
        cor = COR_ACERTO if acertou else COR_ERRO
        titulo = "Acertou! O chefe perdeu 1 coração." if acertou else "Errou! Você perdeu 1 coração."
        _texto(buf, titulo, self.fonte_titulo, cor, (x, y))
        # A explicação aparece nos dois casos: no erro ensina, no acerto reforça o porquê.
        _linhas(buf, quebrar_texto(duelo.explicacao, self.fonte_pequena, largura),
                self.fonte_pequena, COR_TEXTO, x, y + 38, 24, 4)

        if duelo.venceu:
            rodape = "Você derrotou o chefe! Enter para continuar"
        elif duelo.game_over:
            rodape = "Fim de jogo. Enter para continuar"
        else:
            rodape = "Enter para continuar"
        if self.tempo_fase >= ESPERA_MINIMA:
            _texto(buf, rodape, self.fonte_pequena, COR_TEXTO,
                   (PAINEL.width // 2, PAINEL.height - 22), centro=True)


class TelaAndarConcluido:
    """Depois de vencer um chefe: mostra as estrelas do duelo (1 a 3, pelos corações que sobraram).
    Se ainda dá para ganhar mais estrelas, oferece uma nova chance no mesmo andar.

    Teclado: ↑/↓ (ou ←/→) escolhem, 1 e 2 também, Enter confirma. Mouse: passar por cima destaca e
    clicar confirma. Ao terminar, `acao` é "repetir" ou "continuar"."""

    def __init__(self, andar, estrelas, melhor, pode_repetir):
        self.andar = andar
        self.estrelas = estrelas
        self.melhor = melhor
        self.acoes = ["repetir", "continuar"] if pode_repetir else ["continuar"]
        self.selecionada = len(self.acoes) - 1   # começa em "Continuar", para não repetir sem querer
        self.concluida = False
        self.acao = None
        self.tempo = 0.0
        self.fala = CHEFES_INFOS.get(andar, {}).get("fala_derrota", "")

        self.fundo = carregar_imagem(FUNDOS_ANDAR.get(andar), (WIDTH, HEIGHT)).copy()
        escuro = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        escuro.fill((0, 0, 0, 150))
        self.fundo.blit(escuro, (0, 0))
        self.fonte_titulo = carregar_fonte(38, negrito=True)
        self.fonte_texto = carregar_fonte(22)
        self.fonte_estrelas = carregar_fonte(28, negrito=True)
        self.fonte_opcao = carregar_fonte(22)
        tocar_som(SOM_VITORIA)

    def _retangulo_opcao(self, i):
        rect = pygame.Rect(0, 0, 500, 46)
        rect.center = (PAINEL_ESTRELAS.centerx, PAINEL_ESTRELAS.bottom - 100 + i * 56 - (len(self.acoes) - 1) * 28)
        return rect

    def _opcao_sob(self, pos):
        for i in range(len(self.acoes)):
            if self._retangulo_opcao(i).collidepoint(pos):
                return i
        return None

    def _confirmar(self):
        self.acao = self.acoes[self.selecionada]
        self.concluida = True

    def tratar_evento(self, evento):
        if self.tempo < ANDAR_CONCLUIDO_ESPERA or self.concluida:
            return
        n = len(self.acoes)
        if evento.type == pygame.MOUSEMOTION:
            i = self._opcao_sob(evento.pos)
            if i is not None:
                self.selecionada = i
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            i = self._opcao_sob(evento.pos)
            if i is not None:
                self.selecionada = i
                self._confirmar()
        elif evento.type == pygame.KEYDOWN:
            if evento.key in (pygame.K_UP, pygame.K_LEFT):
                self.selecionada = (self.selecionada - 1) % n
            elif evento.key in (pygame.K_DOWN, pygame.K_RIGHT):
                self.selecionada = (self.selecionada + 1) % n
            elif pygame.K_1 <= evento.key <= pygame.K_2 and evento.key - pygame.K_1 < n:
                self.selecionada = evento.key - pygame.K_1
            elif evento.key in ENTER:
                self._confirmar()

    def atualizar(self, dt):
        self.tempo += dt

    def desenhar(self, tela):
        tela.blit(self.fundo, (0, 0))
        painel = PAINEL_ESTRELAS
        pygame.draw.rect(tela, COR_PAINEL, painel, border_radius=14)
        pygame.draw.rect(tela, COR_OURO, painel, width=3, border_radius=14)
        meio = painel.centerx

        _texto(tela, f"ANDAR {self.andar} CONCLUÍDO!", self.fonte_titulo, COR_OURO, (meio, painel.y + 52), centro=True)
        y = painel.y + 100
        for linha in quebrar_texto(self.fala, self.fonte_texto, painel.width - 80)[:3]:
            _texto(tela, linha, self.fonte_texto, COR_TEXTO, (meio, y), centro=True)
            y += 30

        for i in range(3):  # as estrelas ganhas ficam douradas
            desenhar_estrela(tela, (meio + (i - 1) * 130, painel.y + 232), 48, i < self.estrelas)
        _texto(tela, f"{self.estrelas} de 3 estrelas", self.fonte_estrelas, COR_TEXTO, (meio, painel.y + 308), centro=True)
        _texto(tela, f"Melhor deste andar: {self.melhor} de 3", self.fonte_texto, COR_TEXTO,
               (meio, painel.y + 346), centro=True)

        for i, acao in enumerate(self.acoes):
            rect = self._retangulo_opcao(i)
            ativa = i == self.selecionada
            pygame.draw.rect(tela, COR_SELECIONADA if ativa else COR_PAINEL, rect, border_radius=8)
            pygame.draw.rect(tela, COR_TEXTO if ativa else COR_BORDA, rect, width=2, border_radius=8)
            _texto(tela, f"{i + 1}  {ROTULOS_ACAO[acao]}", self.fonte_opcao, COR_TEXTO, rect.center, centro=True)


class TelaBau:
    """Pergunta do baú da exploração (aparece por cima da exploração). Responder certo dá 1 coração extra.

    Mesmo sistema do duelo: escolhe com ↑↓ ou 1 a 4 (ou passando o mouse); Enter ou clique na alternativa
    pergunta "Confirmar a resposta?", e só Confirmar vale (Cancelar ou Backspace voltam às alternativas).
    Depois mostra o resultado e a explicação; Enter ou clique fecham. `acertou` fica True ou False e `concluida` vira True ao fechar."""

    def __init__(self, pergunta):
        self.pergunta = pergunta
        self.selecionada = 0
        self.confirmando = False      # True: perguntando "Confirmar a resposta?" antes de valer
        self.foco_confirmar = 0       # 0 = Confirmar, 1 = Cancelar
        self.respondida = False
        self.acertou = None
        self.concluida = False
        self.tempo_resultado = 0.0
        self.fonte_titulo = carregar_fonte(30, negrito=True)
        self.fonte_enunciado = carregar_fonte(24)
        self.fonte_opcao = carregar_fonte(22)
        self.fonte_pequena = carregar_fonte(20)
        self.fonte_dica = carregar_fonte(16)
        self.escuro = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.escuro.fill((0, 0, 0, 170))

    def _retangulos_opcoes(self):
        largura = PAINEL_BAU.width - 2 * PAINEL_MARGEM
        linhas = quebrar_texto(self.pergunta["enunciado"], self.fonte_enunciado, largura)
        topo = PAINEL_BAU.y + 70 + min(len(linhas), 5) * 30 + 16
        return [pygame.Rect(PAINEL_BAU.x + PAINEL_MARGEM, topo + i * OPCAO_ESPACO, largura, OPCAO_ALTURA)
                for i in range(len(self.pergunta["opcoes"]))]

    def _opcao_sob(self, pos):
        for i, rect in enumerate(self._retangulos_opcoes()):
            if rect.collidepoint(pos):
                return i
        return None

    def _botoes_confirmacao(self):
        topo = self._retangulos_opcoes()[-1].bottom + 16
        return _botoes_de_confirmacao(topo, PAINEL_BAU.centerx, self.fonte_titulo.get_height())

    def _botao_sob(self, pos):
        for i, rect in enumerate(self._botoes_confirmacao()):
            if rect.collidepoint(pos):
                return i
        return None

    def _perguntar_confirmacao(self):
        self.confirmando = True
        self.foco_confirmar = 0

    def _aplicar_confirmacao(self):
        self.confirmando = False
        if self.foco_confirmar == 0:
            self._responder()

    def _responder(self):
        self.respondida = True
        self.acertou = self.selecionada == self.pergunta["correta"]
        tocar_som(SOM_ACERTO if self.acertou else SOM_ERRO)

    def _fechar(self):
        if self.tempo_resultado >= BAU_ESPERA:
            self.concluida = True

    def tratar_evento(self, evento):
        n = len(self.pergunta["opcoes"])
        if self.respondida:
            if (evento.type == pygame.KEYDOWN and evento.key in ENTER) or (
                    evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1):
                self._fechar()
            return
        if evento.type == pygame.MOUSEMOTION:
            if self.confirmando:
                b = self._botao_sob(evento.pos)
                if b is not None:
                    self.foco_confirmar = b
            else:
                i = self._opcao_sob(evento.pos)
                if i is not None:
                    self.selecionada = i
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.confirmando:
                b = self._botao_sob(evento.pos)
                if b is not None:
                    self.foco_confirmar = b
                    self._aplicar_confirmacao()
            else:
                i = self._opcao_sob(evento.pos)
                if i is not None:
                    self.selecionada = i
                    self._perguntar_confirmacao()
        elif evento.type == pygame.KEYDOWN and self.confirmando:
            if evento.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN):
                self.foco_confirmar = 1 - self.foco_confirmar
            elif evento.key in ENTER:
                self._aplicar_confirmacao()
            elif evento.key == pygame.K_BACKSPACE:
                self.confirmando = False
            elif pygame.K_1 <= evento.key <= pygame.K_4 and evento.key - pygame.K_1 < n:
                self.selecionada = evento.key - pygame.K_1    # escolher outra alternativa desfaz a pergunta
                self.confirmando = False
        elif evento.type == pygame.KEYDOWN:
            if evento.key in (pygame.K_UP, pygame.K_w):
                self.selecionada = (self.selecionada - 1) % n
            elif evento.key in (pygame.K_DOWN, pygame.K_s):
                self.selecionada = (self.selecionada + 1) % n
            elif pygame.K_1 <= evento.key <= pygame.K_4 and evento.key - pygame.K_1 < n:
                self.selecionada = evento.key - pygame.K_1
            elif evento.key in ENTER:
                self._perguntar_confirmacao()

    def atualizar(self, dt):
        if self.respondida:
            self.tempo_resultado += dt

    def _cor_da_opcao(self, i):
        if self.respondida:
            if i == self.pergunta["correta"]:
                return COR_ACERTO, COR_TEXTO
            if i == self.selecionada:
                return COR_ERRO, COR_TEXTO
        elif i == self.selecionada:
            return COR_SELECIONADA, COR_TEXTO
        return COR_PAINEL, COR_BORDA

    def desenhar(self, tela):
        tela.blit(self.escuro, (0, 0))
        pygame.draw.rect(tela, COR_PAINEL, PAINEL_BAU, border_radius=14)
        pygame.draw.rect(tela, COR_OURO, PAINEL_BAU, width=4, border_radius=14)
        meio = PAINEL_BAU.centerx
        _texto(tela, "BAÚ DO TESOURO", self.fonte_titulo, COR_OURO, (meio, PAINEL_BAU.y + 30), centro=True)

        x = PAINEL_BAU.x + PAINEL_MARGEM
        largura = PAINEL_BAU.width - 2 * PAINEL_MARGEM
        linhas = quebrar_texto(self.pergunta["enunciado"], self.fonte_enunciado, largura)
        _linhas(tela, linhas, self.fonte_enunciado, COR_TEXTO, x, PAINEL_BAU.y + 62, 30, 5)

        retangulos = self._retangulos_opcoes()
        for i, (opcao, rect) in enumerate(zip(self.pergunta["opcoes"], retangulos)):
            fundo, borda = self._cor_da_opcao(i)
            pygame.draw.rect(tela, fundo, rect, border_radius=8)
            pygame.draw.rect(tela, borda, rect, width=2, border_radius=8)
            _texto(tela, f"{i + 1}  {opcao}", self.fonte_opcao, COR_TEXTO,
                   (rect.x + 14, rect.centery - self.fonte_opcao.get_height() // 2))
        y = retangulos[-1].bottom + 14

        if not self.respondida:
            if self.confirmando:
                _desenhar_confirmacao_comum(tela, f"Confirmar a resposta {self.selecionada + 1}?", self.fonte_titulo,
                                            self.fonte_opcao, retangulos[-1].bottom + 16, meio, self.foco_confirmar)
            dica = DICA_CONFIRMAR if self.confirmando else "↑ ↓ ou 1 a 4: escolher   ·   Enter ou clique: responder"
            _texto(tela, dica, self.fonte_dica, (170, 160, 190), (meio, PAINEL_BAU.bottom - 22), centro=True)
            return
        if self.acertou:
            _texto(tela, "Acertou! +1 coração!", self.fonte_titulo, COR_ACERTO, (x, y))
        else:
            _texto(tela, "Errou. O baú estava vazio.", self.fonte_titulo, COR_ERRO, (x, y))
        _linhas(tela, quebrar_texto(self.pergunta["explicacao"], self.fonte_pequena, largura),
                self.fonte_pequena, COR_TEXTO, x, y + 40, 24, 3)
        if self.tempo_resultado >= BAU_ESPERA:
            _texto(tela, "Enter para continuar", self.fonte_pequena, COR_TEXTO, (meio, PAINEL_BAU.bottom - 22), centro=True)


class TelaPausa:
    """Menu de pausa (ESC): Continuar, Som ligado/desligado, Voltar ao menu e Sair do jogo.

    Não guarda o jogo: o main só para de atualizar a tela de baixo enquanto ela está aberta.
    `tratar_evento` devolve a ação escolhida ("continuar", "som", "menu" ou "sair") ou None.
    ESC de novo também continua. Teclado (↑↓ ou W/S, Enter, 1 a 4) e mouse."""

    def __init__(self):
        self.selecionada = 0
        self.fonte_titulo = carregar_fonte(38, negrito=True)
        self.fonte_opcao = carregar_fonte(22)
        self.escuro = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.escuro.fill((0, 0, 0, 170))

    def rotulo(self, acao):
        return {
            "continuar": "Continuar",
            "som": "Som: desligado" if som_mudo() else "Som: ligado",
            "menu": "Voltar ao menu",
            "sair": "Sair do jogo",
        }[acao]

    def _retangulo_opcao(self, i):
        return pygame.Rect(PAINEL_PAUSA.x + 40, PAINEL_PAUSA.y + 110 + i * 62, PAINEL_PAUSA.width - 80, 50)

    def _opcao_sob(self, pos):
        for i in range(len(ACOES_PAUSA)):
            if self._retangulo_opcao(i).collidepoint(pos):
                return i
        return None

    def tratar_evento(self, evento):
        n = len(ACOES_PAUSA)
        if evento.type == pygame.MOUSEMOTION:
            i = self._opcao_sob(evento.pos)
            if i is not None:
                self.selecionada = i
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            i = self._opcao_sob(evento.pos)
            if i is not None:
                self.selecionada = i
                return ACOES_PAUSA[i]
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                return "continuar"
            if evento.key in (pygame.K_UP, pygame.K_w):
                self.selecionada = (self.selecionada - 1) % n
            elif evento.key in (pygame.K_DOWN, pygame.K_s):
                self.selecionada = (self.selecionada + 1) % n
            elif pygame.K_1 <= evento.key <= pygame.K_4:
                self.selecionada = evento.key - pygame.K_1
                return ACOES_PAUSA[self.selecionada]
            elif evento.key in ENTER:
                return ACOES_PAUSA[self.selecionada]
        return None

    def desenhar(self, tela):
        tela.blit(self.escuro, (0, 0))
        pygame.draw.rect(tela, COR_PAINEL, PAINEL_PAUSA, border_radius=14)
        pygame.draw.rect(tela, COR_BORDA, PAINEL_PAUSA, width=4, border_radius=14)
        _texto(tela, "PAUSA", self.fonte_titulo, COR_TEXTO, (PAINEL_PAUSA.centerx, PAINEL_PAUSA.y + 55), centro=True)
        for i, acao in enumerate(ACOES_PAUSA):
            rect = self._retangulo_opcao(i)
            ativa = i == self.selecionada
            pygame.draw.rect(tela, COR_SELECIONADA if ativa else COR_PAINEL, rect, border_radius=8)
            pygame.draw.rect(tela, COR_TEXTO if ativa else COR_BORDA, rect, width=2, border_radius=8)
            _texto(tela, f"{i + 1}  {self.rotulo(acao)}", self.fonte_opcao, COR_TEXTO, rect.center, centro=True)


class TelaGameOver:
    """Tela preta com "GAME OVER" em vermelho. Depois de 2 segundos aparece, no canto inferior
    direito, "Aperte enter para recomeçar". Só o Enter (ou um clique) depois da mensagem vale e leva ao menu."""

    def __init__(self):
        self.concluida = False
        self.acao = None
        self.tempo = 0.0
        self.fonte_titulo = carregar_fonte(130, negrito=True)
        self.fonte_mensagem = carregar_fonte(28)
        tocar_som(SOM_GAME_OVER)

    @property
    def mensagem_visivel(self):
        return self.tempo >= GAME_OVER_ATRASO

    def tratar_evento(self, evento):
        apertou = evento.type == pygame.KEYDOWN and evento.key in ENTER
        clicou = evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1
        if (apertou or clicou) and self.mensagem_visivel:
            self.acao = "menu"
            self.concluida = True

    def atualizar(self, dt):
        self.tempo += dt

    def desenhar(self, tela):
        tela.fill((0, 0, 0))
        _texto(tela, "GAME OVER", self.fonte_titulo, COR_GAME_OVER, (WIDTH // 2, HEIGHT // 2), centro=True)
        if self.mensagem_visivel:
            imagem = self.fonte_mensagem.render("Aperte enter para recomeçar", True, COR_TEXTO)
            tela.blit(imagem, imagem.get_rect(bottomright=(WIDTH - 32, HEIGHT - 28)))
