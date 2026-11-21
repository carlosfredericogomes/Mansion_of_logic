"""Telas de exploração, pergunta, combate e game over (pygame). Só desenham e leem o teclado:
quem decide o dano é o Duelo, em regras.py."""
import math

import pygame

from config.config import (
    ALTURA_JOGADOR_MEDIA, COR_ACERTO, COR_BORDA, COR_CORACAO, COR_DANO, COR_ERRO, COR_GAME_OVER, COR_PAINEL,
    COR_SELECIONADA, COR_TEXTO, HEIGHT, WIDTH,
)
from src.recursos import (
    CHEFES_SPRITE, FUNDOS_ANDAR, FUNDOS_EXPLORACAO, JOGADOR_COSTAS_SPRITE, JOGADOR_SPRITE,
    carregar_fonte, carregar_imagem, redimensionar_por_altura,
)
from src.chefes import CHEFES

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
TAMANHO_JOGADOR = (192, 240)
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

    def __init__(self, andar=1):
        self.andar = andar
        self.cenas = CENAS_POR_ANDAR[andar]
        self.tempo_andando = 0.0  # só conta enquanto anda, para o ritmo dos passos
        self.andando = False
        self.concluida = False
        self.fundos = [carregar_imagem(nome, (WIDTH, HEIGHT)) for nome in FUNDOS_EXPLORACAO[andar]]
        self.sprite = _sprite_com_pivo_nos_pes(carregar_imagem(JOGADOR_COSTAS_SPRITE), ALTURA_REF_EXPLORADOR)
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

    def tratar_evento(self, evento):
        if evento.type == pygame.KEYDOWN and (evento.key in ENTER or evento.key == pygame.K_SPACE):
            self.concluida = True  # pula a exploração

    def atualizar(self, dt, teclas=None):
        """`teclas` é o estado do teclado (pygame.key.get_pressed()); os testes passam o seu."""
        if self.concluida:
            return
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

        cena = self.cenas[self.cena]
        y_ini, y_fim = cena["y"]
        velocidade_frente = (y_ini - y_fim) / cena["tempo"]
        velocidade_lado = VELOCIDADE_LATERAL * self._escala_bruta() / cena["escala"][0]  # mais devagar ao longe
        self.y = max(float(y_fim), min(float(y_ini), self.y + dy * velocidade_frente * dt))
        self.x = self._limitar_x(self.x + dx * velocidade_lado * dt)

        self.andando = bool(dx or dy)
        if self.andando:
            self.tempo_andando += dt
        if self.y <= y_fim:
            self.fade_saida = 0.0

    def desenhar(self, superficie):
        escala = self._escala_bruta() * ESCALA_EXPLORADOR
        angulo = 0.0
        if self.andando:  # passos: o corpo balança de lado e "pesa", com os pés parados no chão
            fase = self.tempo_andando * PASSOS_POR_SEGUNDO * math.pi
            angulo = 3.0 * math.sin(fase)
            escala *= 1.0 + 0.03 * abs(math.sin(fase))
        figura = pygame.transform.rotozoom(self.sprite, angulo, escala)

        superficie.blit(self.fundos[self.cena], (0, 0))
        superficie.blit(figura, figura.get_rect(center=(round(self.x), round(self.y))))

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
        self.fonte_titulo = carregar_fonte(26, negrito=True)

    def _ir_para(self, fase):
        self.fase = fase
        self.tempo_fase = 0.0

    def _sincronizar_coracoes(self):
        self.vidas_jogador_ex = self.duelo.vidas_jogador
        self.vidas_chefe_ex = self.duelo.vidas_chefe

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
                self._ir_para(FASE_PISCADA)
        elif self.fase == FASE_RESULTADO and evento.key in ENTER and self.tempo_fase >= ESPERA_MINIMA:
            if self.duelo.terminou:
                self.concluida = True
            else:
                self.duelo.proxima_pergunta()
                self.selecionada = 0
                self.escolhida = None
                self._ir_para(FASE_PERGUNTA)

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
        y = _linhas(buf, linhas, self.fonte_enunciado, COR_TEXTO, x, 18, 30, 5) + 16

        for i, opcao in enumerate(pergunta["opcoes"]):
            rect = pygame.Rect(x, y + i * OPCAO_ESPACO, largura, OPCAO_ALTURA)
            fundo, borda = self._cor_da_opcao(i, pergunta)
            pygame.draw.rect(buf, fundo, rect, border_radius=8)
            pygame.draw.rect(buf, borda, rect, width=2, border_radius=8)
            _texto(buf, f"{i + 1}  {opcao}", self.fonte_opcao, COR_TEXTO,
                   (rect.x + 14, rect.centery - self.fonte_opcao.get_height() // 2))
        y += len(pergunta["opcoes"]) * OPCAO_ESPACO + 10

        if self.fase == FASE_RESULTADO:
            self._desenhar_resultado(buf, x, y, largura)
        superficie.blit(buf, (PAINEL.x, PAINEL.y + round(deslocamento)))

    def _desenhar_resultado(self, buf, x, y, largura):
        duelo = self.duelo
        acertou = duelo.ultimo_acertou
        cor = COR_ACERTO if acertou else COR_ERRO
        titulo = "Acertou! O chefe perdeu 1 coração." if acertou else "Errou! Você perdeu 1 coração."
        _texto(buf, titulo, self.fonte_titulo, cor, (x, y))
        if not acertou:
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


class TelaGameOver:
    """Tela preta com "GAME OVER" em vermelho. Depois de 2 segundos aparece, no canto inferior
    direito, "Aperte enter para recomeçar". Só o Enter (depois da mensagem) vale e leva ao menu."""

    def __init__(self):
        self.concluida = False
        self.acao = None
        self.tempo = 0.0
        self.fonte_titulo = carregar_fonte(130, negrito=True)
        self.fonte_mensagem = carregar_fonte(28)

    @property
    def mensagem_visivel(self):
        return self.tempo >= GAME_OVER_ATRASO

    def tratar_evento(self, evento):
        if evento.type == pygame.KEYDOWN and evento.key in ENTER and self.mensagem_visivel:
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
