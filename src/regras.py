import random
from enum import Enum, auto
from src.chefes import CHEFES, CUSTO_ACERTO, CUSTO_ERRO, JOGADOR_VIDAS
from src.questoes import carregar_perguntas


class Estado(Enum):
    S0_EXPLORACAO = auto()
    S1_PERGUNTA = auto()
    S2_AVALIACAO = auto()
    S3_DANO_CHEFE = auto()
    S4_DANO_JOGADOR = auto()
    S5_AVANCO_ANDAR = auto()
    S6_GAME_OVER = auto()

class Evento(Enum):
    ENCONTRO_CHEFE = auto()
    CONFIRMOU_RESPOSTA = auto()
    ACERTOU = auto()
    ERROU = auto()
    CHEFE_SEM_VIDAS = auto()
    CHEFE_COM_VIDAS = auto()
    JOGADOR_SEM_VIDAS = auto()
    JOGADOR_COM_VIDAS = auto()


TRANSICOES = {
    (Estado.S0_EXPLORACAO, Evento.ENCONTRO_CHEFE): Estado.S1_PERGUNTA,
    (Estado.S1_PERGUNTA, Evento.CONFIRMOU_RESPOSTA): Estado.S2_AVALIACAO,
    (Estado.S2_AVALIACAO, Evento.ACERTOU): Estado.S3_DANO_CHEFE,
    (Estado.S2_AVALIACAO, Evento.ERROU): Estado.S4_DANO_JOGADOR,
    (Estado.S3_DANO_CHEFE, Evento.CHEFE_SEM_VIDAS): Estado.S5_AVANCO_ANDAR,
    (Estado.S3_DANO_CHEFE, Evento.CHEFE_COM_VIDAS): Estado.S1_PERGUNTA,
    (Estado.S4_DANO_JOGADOR, Evento.JOGADOR_SEM_VIDAS): Estado.S6_GAME_OVER,
    (Estado.S4_DANO_JOGADOR, Evento.JOGADOR_COM_VIDAS): Estado.S1_PERGUNTA,
}

def proximo_estado(estado, evento):
    try:
        return TRANSICOES[(estado, evento)]
    except KeyError:
        raise ValueError(f"Transição inválida: {estado.name} com {evento.name}") from None

def verificar_resposta(pergunta, indice_escolhido):
    return indice_escolhido == pergunta["correta"]
class BancoInsuficiente(RuntimeError):
    """O banco de perguntas acabou antes do fim do duelo."""

def embaralhar_opcoes(pergunta):
    """Devolve uma cópia da pergunta com as opções embaralhadas e 'correta' recalculada."""
    ordem = list(range(len(pergunta["opcoes"])))
    random.shuffle(ordem)
    copia = dict(pergunta)
    copia["opcoes"] = [pergunta["opcoes"][i] for i in ordem]
    copia["correta"] = ordem.index(pergunta["correta"])
    return copia

class Duelo:
    """Duelo de perguntas entre o Exterminador e o chefe de um andar (sem pygame).

    Fluxo: o duelo começa em S1 (pergunta apresentada). `responder` aplica o dano
    e avança a máquina de estados; se o duelo continua, o estado volta a S1 e quem
    chama usa `proxima_pergunta()` para sortear a seguinte.
    """

    def __init__(self, andar, vidas_jogador=JOGADOR_VIDAS, perguntas=None):
        if andar not in CHEFES:
            raise ValueError(f"Andar inválido: {andar!r}")
        self.andar = andar
        self.vidas_jogador = vidas_jogador
        self.vidas_chefe = CHEFES[andar]["vidas"]

        banco = list(perguntas) if perguntas is not None else carregar_perguntas(andar)
        random.shuffle(banco)
        self._restantes = banco  # sorteadas por pop(): nenhuma repete no duelo

        self.estado = proximo_estado(Estado.S0_EXPLORACAO, Evento.ENCONTRO_CHEFE)  # S1
        self.pergunta_atual = None
        self.ultima_pergunta = None  # a que acabou de ser respondida (para a tela mostrar a explicação)
        self.ultimo_acertou = None
        self.proxima_pergunta()

    @property
    def terminou(self):
        return self.estado in (Estado.S5_AVANCO_ANDAR, Estado.S6_GAME_OVER)

    @property
    def venceu(self):
        return self.estado == Estado.S5_AVANCO_ANDAR

    @property
    def game_over(self):
        return self.estado == Estado.S6_GAME_OVER

    @property
    def explicacao(self):
        """Explicação da última pergunta respondida (a tela mostra depois de um erro)."""
        return self.ultima_pergunta["explicacao"] if self.ultima_pergunta else None

    def proxima_pergunta(self):
        if self.estado != Estado.S1_PERGUNTA:
            raise ValueError(f"Não há próxima pergunta no estado {self.estado.name}")
        if not self._restantes:
            raise BancoInsuficiente(
                f"Andar {self.andar}: o banco de perguntas acabou antes do fim do duelo "
                f"(chefe com {self.vidas_chefe} e jogador com {self.vidas_jogador} corações)."
            )
        self.pergunta_atual = embaralhar_opcoes(self._restantes.pop())
        return self.pergunta_atual

    def responder(self, indice_escolhido):
        """Aplica a resposta. Devolve True se acertou. Só vale em S1 (com pergunta apresentada)."""
        if self.estado != Estado.S1_PERGUNTA:
            raise ValueError(f"Não é possível responder no estado {self.estado.name}")

        self.estado = proximo_estado(self.estado, Evento.CONFIRMOU_RESPOSTA)  # S2
        acertou = verificar_resposta(self.pergunta_atual, indice_escolhido)
        self.estado = proximo_estado(self.estado, Evento.ACERTOU if acertou else Evento.ERROU)

        if acertou:
            self.vidas_chefe = max(0, self.vidas_chefe - CUSTO_ACERTO)  # S3
            evento = Evento.CHEFE_SEM_VIDAS if self.vidas_chefe == 0 else Evento.CHEFE_COM_VIDAS
        else:
            self.vidas_jogador = max(0, self.vidas_jogador - CUSTO_ERRO)  # S4
            evento = Evento.JOGADOR_SEM_VIDAS if self.vidas_jogador == 0 else Evento.JOGADOR_COM_VIDAS
        self.estado = proximo_estado(self.estado, evento)

        self.ultima_pergunta = self.pergunta_atual
        self.ultimo_acertou = acertou
        return acertou