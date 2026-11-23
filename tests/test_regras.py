import pytest
import json
import random

from src.chefes import CHEFES, CUSTO_ACERTO, CUSTO_ERRO, JOGADOR_VIDAS
from src.questoes import carregar_perguntas, validar_pergunta
from src.regras import (
    BancoInsuficiente, Duelo, Estado, Evento, TRANSICOES, embaralhar_opcoes,
    proximo_estado, verificar_resposta,
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


# --- Carregador de perguntas (c22) ---

PERGUNTA_OK = {
    "id": 1, "enunciado": "Pergunta?", "opcoes": ["a", "b"], "correta": 1, "explicacao": "Porque sim.",
}


def test_validar_pergunta_aceita_formato_correto():
    validar_pergunta(PERGUNTA_OK)


@pytest.mark.parametrize("alteracao", [
    {"opcoes": ["so uma"], "correta": 0},          # menos de 2 opções
    {"opcoes": ["a", "b", "c", "d", "e"]},         # mais de 4 opções
    {"correta": 2},                                # fora de opcoes
    {"correta": -1},                               # negativa
    {"correta": "0"},                              # não é número
])
def test_validar_pergunta_rejeita_formato_invalido(alteracao):
    with pytest.raises(ValueError):
        validar_pergunta({**PERGUNTA_OK, **alteracao})


@pytest.mark.parametrize("campo", ["id", "enunciado", "opcoes", "correta", "explicacao"])
def test_validar_pergunta_exige_campos(campo):
    pergunta = {k: v for k, v in PERGUNTA_OK.items() if k != campo}
    with pytest.raises(ValueError):
        validar_pergunta(pergunta)


def test_carregar_perguntas_avisa_se_faltar_pergunta(tmp_path, monkeypatch):
    (tmp_path / "andar_1.json").write_text(json.dumps([PERGUNTA_OK]), encoding="utf-8")
    monkeypatch.setattr("src.questoes.PERGUNTAS_DIR", tmp_path)
    with pytest.warns(UserWarning, match="(?i)andar 1"):
        assert len(carregar_perguntas(1)) == 1


def test_carregar_perguntas_avisa_se_arquivo_nao_existe(tmp_path, monkeypatch):
    monkeypatch.setattr("src.questoes.PERGUNTAS_DIR", tmp_path)
    with pytest.warns(UserWarning, match="não encontrado"):
        assert carregar_perguntas(1) == []


# --- Motor de duelo (c23 / c24) ---

def _acertar(duelo):
    return duelo.responder(duelo.pergunta_atual["correta"])


def _errar(duelo):
    p = duelo.pergunta_atual
    return duelo.responder((p["correta"] + 1) % len(p["opcoes"]))


def _seguir(duelo):
    """Sorteia a próxima pergunta se o duelo continua."""
    if duelo.estado == Estado.S1_PERGUNTA:
        duelo.proxima_pergunta()


def test_duelo_comeca_em_s1_com_as_vidas_decididas():
    duelo = Duelo(1)
    assert duelo.estado == Estado.S1_PERGUNTA
    assert duelo.vidas_jogador == JOGADOR_VIDAS == 3
    assert duelo.vidas_chefe == CHEFES[1]["vidas"] == 3
    assert duelo.pergunta_atual is not None


def test_duelo_aceita_vidas_iniciais_do_jogador_como_parametro():
    assert Duelo(1, vidas_jogador=2).vidas_jogador == 2


def test_erro_tira_exatamente_1_coracao_do_jogador_e_nenhum_do_chefe():
    duelo = Duelo(2)
    assert _errar(duelo) is False
    assert duelo.vidas_jogador == JOGADOR_VIDAS - CUSTO_ERRO
    assert duelo.vidas_chefe == CHEFES[2]["vidas"]


def test_acerto_tira_1_coracao_do_chefe_e_nenhum_do_jogador():
    duelo = Duelo(2)
    assert _acertar(duelo) is True
    assert duelo.vidas_chefe == CHEFES[2]["vidas"] - CUSTO_ACERTO
    assert duelo.vidas_jogador == JOGADOR_VIDAS


def test_tres_erros_seguidos_levam_ao_game_over_s6():
    duelo = Duelo(1)
    for restantes in (2, 1):
        _errar(duelo)
        assert duelo.vidas_jogador == restantes
        assert duelo.estado == Estado.S1_PERGUNTA
        _seguir(duelo)
    _errar(duelo)
    assert duelo.vidas_jogador == 0
    assert duelo.estado == Estado.S6_GAME_OVER
    assert duelo.game_over and duelo.terminou and not duelo.venceu


def test_vida_do_jogador_nunca_fica_negativa():
    duelo = Duelo(1, vidas_jogador=1)
    _errar(duelo)
    assert duelo.vidas_jogador == 0
    # Depois do game over não dá para responder mais, então a vida não passa de 0.
    with pytest.raises(ValueError):
        duelo.responder(0)
    assert duelo.vidas_jogador == 0


def test_nao_responde_nem_sorteia_depois_do_fim():
    duelo = Duelo(1)
    for _ in range(CHEFES[1]["vidas"]):
        _acertar(duelo)
        _seguir(duelo)
    assert duelo.estado == Estado.S5_AVANCO_ANDAR
    with pytest.raises(ValueError):
        duelo.responder(0)
    with pytest.raises(ValueError):
        duelo.proxima_pergunta()


@pytest.mark.parametrize("andar", [1, 2, 3, 4])
def test_pior_caso_2_erros_e_depois_acertos_vence_com_1_coracao(andar):
    duelo = Duelo(andar)
    perguntas_usadas = 0
    for _ in range(JOGADOR_VIDAS - 1):
        _errar(duelo)
        perguntas_usadas += 1
        _seguir(duelo)
    while not duelo.terminou:
        _acertar(duelo)
        perguntas_usadas += 1
        _seguir(duelo)
    assert duelo.venceu
    assert duelo.vidas_chefe == 0
    assert duelo.vidas_jogador == 1
    assert perguntas_usadas == CHEFES[andar]["vidas"] + JOGADOR_VIDAS - 1


@pytest.mark.parametrize("andar", [1, 2, 3, 4])
def test_nenhuma_pergunta_repete_no_mesmo_duelo(andar):
    random.seed(2026)
    duelo = Duelo(andar)
    ids = []
    for _ in range(JOGADOR_VIDAS - 1):
        ids.append(duelo.pergunta_atual["id"])
        _errar(duelo)
        _seguir(duelo)
    while not duelo.terminou:
        ids.append(duelo.pergunta_atual["id"])
        _acertar(duelo)
        _seguir(duelo)
    assert len(ids) == len(set(ids))


@pytest.mark.parametrize("andar", [1, 2, 3, 4])
def test_embaralhar_mantem_a_opcao_correta(andar):
    random.seed(7)
    for original in carregar_perguntas(andar):
        texto_certo = original["opcoes"][original["correta"]]
        for _ in range(20):
            embaralhada = embaralhar_opcoes(original)
            assert sorted(embaralhada["opcoes"]) == sorted(original["opcoes"])
            assert embaralhada["opcoes"][embaralhada["correta"]] == texto_certo
    # A pergunta original não é alterada.
    assert original["opcoes"][original["correta"]] == texto_certo


def test_resposta_certa_depois_de_embaralhar_acerta():
    random.seed(3)
    for andar in (1, 2, 3, 4):
        duelo = Duelo(andar)
        assert verificar_resposta(duelo.pergunta_atual, duelo.pergunta_atual["correta"])


def test_explicacao_da_ultima_pergunta_fica_guardada():
    duelo = Duelo(1)
    esperado = duelo.pergunta_atual["explicacao"]
    _errar(duelo)
    _seguir(duelo)  # a próxima pergunta já foi sorteada...
    assert duelo.explicacao == esperado  # ...mas a explicação do erro continua disponível
    assert duelo.ultimo_acertou is False


def test_banco_acabando_antes_do_fim_avisa_com_mensagem_clara():
    duelo = Duelo(1, perguntas=[PERGUNTA_OK])
    _errar(duelo)
    with pytest.raises(BancoInsuficiente, match="banco de perguntas acabou"):
        duelo.proxima_pergunta()


@pytest.mark.parametrize("andar, pior_caso", [(1, 5), (2, 6), (3, 7), (4, 9)])
def test_banco_cobre_o_pior_caso_com_1_de_sobra(andar, pior_caso):
    banco = len(carregar_perguntas(andar))
    assert CHEFES[andar]["vidas"] + JOGADOR_VIDAS - 1 == pior_caso
    assert banco == CHEFES[andar]["perguntas"]
    assert banco - pior_caso == 1
    assert banco >= pior_caso


def test_total_de_perguntas_e_31():
    assert sum(len(carregar_perguntas(a)) for a in CHEFES) == 31