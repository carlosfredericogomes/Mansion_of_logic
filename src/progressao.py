"""Progressão entre os andares, estrelas e pontuação (sem pygame).

Quem decide o resultado de cada duelo é o Duelo (regras.py); aqui fica a conta da partida inteira:
em que andar o jogador está, quantas estrelas ganhou em cada andar e o que acontece depois de um duelo."""
from src.chefes import CHEFES, JOGADOR_VIDAS, TOTAL_ANDARES, obter_chefe, perguntas_necessarias
import random

from src.questoes import carregar_perguntas, carregar_perguntas_exploracao
from src.regras import Duelo, embaralhar_opcoes

# O que acontece quando um duelo termina.
ANDAR_CONCLUIDO = "ANDAR_CONCLUIDO"   # venceu o chefe: mostra as estrelas e oferece outra chance
PROXIMO_ANDAR = "PROXIMO_ANDAR"
VITORIA = "VITORIA"
GAME_OVER = "GAME_OVER"

ESTRELAS_POR_ANDAR = 3                              # corações que sobram no fim do duelo = estrelas (1 a 3)
PONTUACAO_MAXIMA = ESTRELAS_POR_ANDAR * TOTAL_ANDARES   # 12


# Baús da exploração: respondendo certo, o jogador ganha 1 coração para os duelos seguintes
# (3 + 1 + 1 = até 5 corações no último andar). Errar não custa nada: o baú só fica vazio.
ANDARES_COM_BAU = (3, 4)          # explorações que levam aos andares 3 e 4
VIDAS_POR_BAU = 1
NIVEIS_DO_BAU = {3: (1, 2), 4: (2, 3)}   # baú do andar 3: perguntas fáceis e médias; do andar 4: médias e difíceis


def estrelas_por_vidas(vidas_restantes):
    """3 corações = 3 estrelas, 2 = 2 estrelas, 1 = 1 estrela (nunca passa de 3 nem fica negativo)."""
    return max(0, min(ESTRELAS_POR_ANDAR, vidas_restantes))


class Partida:
    def __init__(self):
        self.andar_atual = 1
        self.duelo = None
        self.chefes_derrotados = []
        self.venceu_jogo = False
        self.estrelas = {}            # melhor resultado de cada andar: {andar: estrelas}
        self.ultimas_estrelas = 0     # estrelas do duelo que acabou de terminar
        self.vidas_extras = 0         # corações ganhos nos baús (somam aos 3 de cada duelo)
        self.baus_abertos = set()     # andares cujo baú já foi aberto
        self._baus_usadas = set()     # ids das perguntas de baú já sorteadas (não repetem na partida)

    @property
    def chefe_atual(self):
        return obter_chefe(self.andar_atual)

    @property
    def melhor_do_andar(self):
        return self.estrelas.get(self.andar_atual, 0)

    @property
    def pode_repetir(self):
        """Só vale a pena tentar de novo quando ainda dá para ganhar mais estrelas neste andar."""
        return self.melhor_do_andar < ESTRELAS_POR_ANDAR

    @property
    def vidas_iniciais(self):
        """Corações com que cada duelo começa: os 3 de sempre mais os ganhos nos baús."""
        return JOGADOR_VIDAS + self.vidas_extras

    @property
    def andar_tem_bau(self):
        """A exploração que leva ao andar atual tem um baú ainda fechado?"""
        return self.andar_atual in ANDARES_COM_BAU and self.andar_atual not in self.baus_abertos

    def sortear_pergunta_bau(self, banco=None):
        """Sorteia a pergunta do baú deste andar (com as alternativas embaralhadas), sem repetir na partida."""
        niveis = NIVEIS_DO_BAU.get(self.andar_atual, (1, 2, 3))
        if banco is None:
            banco = carregar_perguntas_exploracao(niveis)
        candidatas = [p for p in banco if p["id"] not in self._baus_usadas] or list(banco)
        if not candidatas:
            raise RuntimeError("o banco de perguntas da exploração está vazio")
        pergunta = random.choice(candidatas)
        self._baus_usadas.add(pergunta["id"])
        return embaralhar_opcoes(pergunta)

    def abrir_bau(self, acertou):
        """O baú deste andar foi aberto. Se acertou a pergunta, ganha 1 coração; errar não custa nada."""
        self.baus_abertos.add(self.andar_atual)
        if acertou:
            self.vidas_extras += VIDAS_POR_BAU

    @property
    def pontuacao_final(self):
        return sum(self.estrelas.values())

    def iniciar_duelo(self, perguntas=None):
        if self.venceu_jogo:
            raise RuntimeError("o jogo terminou: o último chefe foi derrotado")
        if self.duelo is not None and not self.duelo.terminou:
            raise RuntimeError("já existe um duelo em andamento")
        # Todo duelo começa com os corações cheios: 3, mais os ganhos nos baús (também na nova chance).
        self.duelo = Duelo(self.andar_atual, self.vidas_iniciais, perguntas)
        return self.duelo

    def concluir_duelo(self):
        """Chamar quando o duelo terminou. Devolve GAME_OVER ou ANDAR_CONCLUIDO."""
        if self.duelo is None or not self.duelo.terminou:
            raise RuntimeError("duelo ainda não terminou")
        duelo, self.duelo = self.duelo, None

        if duelo.game_over:
            self.reiniciar()
            return GAME_OVER

        self.ultimas_estrelas = estrelas_por_vidas(duelo.vidas_jogador)
        self.estrelas[duelo.andar] = max(self.melhor_do_andar, self.ultimas_estrelas)  # fica a melhor
        nome = CHEFES[duelo.andar]["nome"]
        if nome not in self.chefes_derrotados:
            self.chefes_derrotados.append(nome)
        return ANDAR_CONCLUIDO

    def avancar(self):
        """Depois de ver as estrelas: vai para o próximo andar ou, depois do último, para a vitória."""
        if self.andar_atual == TOTAL_ANDARES:
            self.venceu_jogo = True
            return VITORIA
        self.andar_atual += 1
        return PROXIMO_ANDAR

    def reiniciar(self):
        self.__init__()


def verificar_relacao_perguntas_chefes(carregador=carregar_perguntas):
    problemas = []
    ids_vistos = {}
    anterior = None

    for andar in range(1, TOTAL_ANDARES + 1):
        chefe = obter_chefe(andar)
        perguntas = carregador(andar)

        if len(perguntas) != chefe["perguntas"]:
            problemas.append(f"andar {andar}: o chefe espera {chefe['perguntas']} perguntas, mas o banco tem {len(perguntas)}")

        minimo = perguntas_necessarias(andar)
        if len(perguntas) < minimo:
            problemas.append(f"andar {andar}: o duelo pode usar até {minimo} perguntas, mas só há {len(perguntas)}; o banco acabaria no meio do duelo")

        if anterior is not None:
            if chefe["vidas"] <= anterior["vidas"]:
                problemas.append(f"andar {andar}: o chefe não tem mais corações que o andar anterior")
            if chefe["perguntas"] <= anterior["perguntas"]:
                problemas.append(f"andar {andar}: o banco não é maior que o do andar anterior")
        anterior = chefe

        for p in perguntas:
            if len(set(p["opcoes"])) != len(p["opcoes"]):
                problemas.append(f"andar {andar}, pergunta {p['id']}: tem alternativas repetidas")
            if p["id"] in ids_vistos:
                problemas.append(f"pergunta {p['id']} aparece nos andares {ids_vistos[p['id']]} e {andar}")
            ids_vistos[p["id"]] = andar

    return problemas
