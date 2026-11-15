from enum import Enum, auto


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