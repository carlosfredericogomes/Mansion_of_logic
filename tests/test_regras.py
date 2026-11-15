import pytest
from src.questoes import carregar_perguntas
from src.regras import (
    Estado, Evento, TRANSICOES, proximo_estado, verificar_resposta,
)


def test_perguntas_validas():
    quantidades = {1: 6, 2: 7, 3: 8, 4: 10}
    
    for andar, qtd in quantidades.items():
        perguntas = carregar_perguntas(andar)
        assert len(perguntas) == qtd
        for p in perguntas:
            assert 0 <= p["correta"] < len(p["opcoes"])


def test_verificar_resposta():
    p = {"correta": 2}
    assert verificar_resposta(p, 2)
    assert not verificar_resposta(p, 0)


TRANSICOES_VALIDAS = [
    (Estado.S0_EXPLORACAO, Evento.ENCONTRO_CHEFE, Estado.S1_PERGUNTA),
    (Estado.S1_PERGUNTA, Evento.CONFIRMOU_RESPOSTA, Estado.S2_AVALIACAO),
    (Estado.S2_AVALIACAO, Evento.ACERTOU, Estado.S3_DANO_CHEFE),
    (Estado.S2_AVALIACAO, Evento.ERROU, Estado.S4_DANO_JOGADOR),
    (Estado.S3_DANO_CHEFE, Evento.CHEFE_SEM_VIDAS, Estado.S5_AVANCO_ANDAR),
    (Estado.S3_DANO_CHEFE, Evento.CHEFE_COM_VIDAS, Estado.S1_PERGUNTA),
    (Estado.S4_DANO_JOGADOR, Evento.JOGADOR_SEM_VIDAS, Estado.S6_GAME_OVER),
    (Estado.S4_DANO_JOGADOR, Evento.JOGADOR_COM_VIDAS, Estado.S1_PERGUNTA),
]


@pytest.mark.parametrize("estado, evento, esperado", TRANSICOES_VALIDAS)
def test_transicao_valida(estado, evento, esperado):
    assert proximo_estado(estado, evento) == esperado


def test_tabela_tem_exatamente_as_8_transicoes():
    assert len(TRANSICOES) == 8


def test_transicao_invalida_levanta_valueerror():
    with pytest.raises(ValueError):
        proximo_estado(Estado.S0_EXPLORACAO, Evento.ERROU)


def _rodada(estado, acertou, vidas_depois):
    """Uma pergunta: S1 -> S2 -> S3/S4 -> (S5/S6 ou volta a S1)."""
    estado = proximo_estado(estado, Evento.CONFIRMOU_RESPOSTA)
    estado = proximo_estado(estado, Evento.ACERTOU if acertou else Evento.ERROU)
    if acertou:
        evento = Evento.CHEFE_SEM_VIDAS if vidas_depois == 0 else Evento.CHEFE_COM_VIDAS
    else:
        evento = Evento.JOGADOR_SEM_VIDAS if vidas_depois == 0 else Evento.JOGADOR_COM_VIDAS
    return proximo_estado(estado, evento)


def test_fluxo_completo_vitoria_no_andar():
    estado = proximo_estado(Estado.S0_EXPLORACAO, Evento.ENCONTRO_CHEFE)
    assert estado == Estado.S1_PERGUNTA
    for vidas_chefe in (2, 1):
        estado = _rodada(estado, acertou=True, vidas_depois=vidas_chefe)
        assert estado == Estado.S1_PERGUNTA
    estado = _rodada(estado, acertou=True, vidas_depois=0)
    assert estado == Estado.S5_AVANCO_ANDAR


def test_fluxo_completo_game_over():
    estado = proximo_estado(Estado.S0_EXPLORACAO, Evento.ENCONTRO_CHEFE)
    for vidas_jogador in (2, 1):
        estado = _rodada(estado, acertou=False, vidas_depois=vidas_jogador)
        assert estado == Estado.S1_PERGUNTA
    estado = _rodada(estado, acertou=False, vidas_depois=0)
    assert estado == Estado.S6_GAME_OVER