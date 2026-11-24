"""Progressão entre os andares, estrelas, pontuação e nova chance (sem pygame)."""
import pytest

from src.chefes import CHEFES, JOGADOR_VIDAS, TOTAL_ANDARES
from src.progressao import (
    ANDAR_CONCLUIDO, ESTRELAS_POR_ANDAR, GAME_OVER, PONTUACAO_MAXIMA, PROXIMO_ANDAR, VITORIA,
    Partida, estrelas_por_vidas, verificar_relacao_perguntas_chefes,
)


def jogar(duelo, plano):
    """Joga um duelo: 'C' = acerta, 'E' = erra. Para quando o duelo termina."""
    for acao in plano:
        p = duelo.pergunta_atual
        escolha = p["correta"] if acao == "C" else (p["correta"] + 1) % len(p["opcoes"])
        duelo.responder(escolha)
        if duelo.terminou:
            return
        duelo.proxima_pergunta()


def vencer_andar(partida, erros=0):
    """Joga o duelo do andar atual errando `erros` vezes antes de derrotar o chefe."""
    duelo = partida.iniciar_duelo()
    jogar(duelo, "E" * erros + "C" * CHEFES[partida.andar_atual]["vidas"])
    assert duelo.venceu
    return partida.concluir_duelo()


# --- Estrelas ---

@pytest.mark.parametrize("vidas, estrelas", [(3, 3), (2, 2), (1, 1), (0, 0), (5, 3), (-1, 0)])
def test_estrelas_pelos_coracoes_que_sobraram(vidas, estrelas):
    assert estrelas_por_vidas(vidas) == estrelas


def test_pontuacao_maxima_e_12():
    assert PONTUACAO_MAXIMA == ESTRELAS_POR_ANDAR * TOTAL_ANDARES == 12


# --- Partida: andar a andar ---

def test_partida_comeca_no_andar_1_sem_estrelas():
    p = Partida()
    assert p.andar_atual == 1 and p.estrelas == {} and p.pontuacao_final == 0 and not p.venceu_jogo


def test_vencer_com_3_coracoes_da_3_estrelas_e_nao_oferece_nova_chance():
    p = Partida()
    assert vencer_andar(p) == ANDAR_CONCLUIDO
    assert p.ultimas_estrelas == 3 and p.estrelas == {1: 3}
    assert not p.pode_repetir
    assert p.chefes_derrotados == [CHEFES[1]["nome"]]


@pytest.mark.parametrize("erros, estrelas", [(0, 3), (1, 2), (2, 1)])
def test_estrelas_dependem_dos_erros(erros, estrelas):
    p = Partida()
    vencer_andar(p, erros=erros)
    assert p.ultimas_estrelas == estrelas
    assert p.pode_repetir == (estrelas < 3)           # só repete se ainda dá para melhorar


def test_avancar_sobe_um_andar():
    p = Partida()
    vencer_andar(p)
    assert p.avancar() == PROXIMO_ANDAR
    assert p.andar_atual == 2


def test_cada_duelo_comeca_com_3_coracoes_cheios():
    p = Partida()
    vencer_andar(p, erros=2)                           # terminou o andar 1 com 1 coração
    p.avancar()
    duelo = p.iniciar_duelo()
    assert duelo.vidas_jogador == JOGADOR_VIDAS == 3 and duelo.vidas_chefe == CHEFES[2]["vidas"]


# --- Outra chance no mesmo andar ---

def test_nova_chance_continua_no_mesmo_andar_com_vidas_cheias():
    p = Partida()
    vencer_andar(p, erros=2)                           # 1 estrela
    assert p.pode_repetir
    duelo = p.iniciar_duelo()                          # tentar de novo, sem avancar()
    assert p.andar_atual == 1
    assert duelo.andar == 1 and duelo.vidas_jogador == 3 and duelo.vidas_chefe == CHEFES[1]["vidas"]


def test_o_andar_fica_com_a_melhor_pontuacao():
    p = Partida()
    vencer_andar(p, erros=2)                           # 1 estrela
    assert p.estrelas[1] == 1
    vencer_andar(p, erros=1)                           # 2 estrelas: melhora
    assert p.estrelas[1] == 2
    vencer_andar(p, erros=2)                           # 1 estrela: não piora
    assert p.estrelas[1] == 2 and p.ultimas_estrelas == 1
    assert p.pontuacao_final == 2


def test_chefe_derrotado_de_novo_nao_duplica_na_lista():
    p = Partida()
    vencer_andar(p, erros=2)
    vencer_andar(p, erros=0)
    assert p.chefes_derrotados == [CHEFES[1]["nome"]]


def test_depois_de_3_estrelas_nao_oferece_mais_nova_chance():
    p = Partida()
    vencer_andar(p, erros=1)
    assert p.pode_repetir
    vencer_andar(p, erros=0)                           # 3 estrelas
    assert not p.pode_repetir


# --- Game over e vitória ---

def test_game_over_na_nova_chance_zera_tudo():
    p = Partida()
    vencer_andar(p)
    p.avancar()
    vencer_andar(p, erros=2)                           # andar 2 com 1 estrela
    duelo = p.iniciar_duelo()
    jogar(duelo, "EEE")                                # perde os 3 corações
    assert duelo.game_over
    assert p.concluir_duelo() == GAME_OVER
    assert p.andar_atual == 1 and p.estrelas == {} and p.pontuacao_final == 0


def test_zerar_o_jogo_da_a_vitoria_e_a_soma_das_estrelas():
    p = Partida()
    for andar in range(1, TOTAL_ANDARES + 1):
        assert p.andar_atual == andar
        assert vencer_andar(p) == ANDAR_CONCLUIDO
        assert p.avancar() == (VITORIA if andar == TOTAL_ANDARES else PROXIMO_ANDAR)
    assert p.venceu_jogo
    assert p.pontuacao_final == PONTUACAO_MAXIMA == 12
    with pytest.raises(RuntimeError):
        p.iniciar_duelo()


def test_pontuacao_final_soma_as_estrelas_de_cada_andar():
    p = Partida()
    for erros in (0, 1, 2, 1):                          # 3 + 2 + 1 + 2 estrelas
        vencer_andar(p, erros=erros)
        p.avancar()
    assert p.pontuacao_final == 8


# --- Proteções ---

def test_nao_inicia_duelo_com_outro_em_andamento():
    p = Partida()
    p.iniciar_duelo()
    with pytest.raises(RuntimeError):
        p.iniciar_duelo()


def test_nao_conclui_duelo_que_nao_terminou():
    p = Partida()
    with pytest.raises(RuntimeError):
        p.concluir_duelo()
    p.iniciar_duelo()
    with pytest.raises(RuntimeError):
        p.concluir_duelo()


# --- Bancos de perguntas x chefes ---

def test_bancos_e_chefes_estao_coerentes():
    assert verificar_relacao_perguntas_chefes() == []


# --- Baús da exploração ---

def _ir_para_o_andar(partida, andar):
    partida.andar_atual = andar
    return partida


def test_so_as_exploracoes_dos_andares_3_e_4_tem_bau():
    p = Partida()
    assert [_ir_para_o_andar(p, a).andar_tem_bau for a in (1, 2, 3, 4)] == [False, False, True, True]


def test_acertar_o_bau_da_um_coracao_e_o_duelo_comeca_com_4():
    p = _ir_para_o_andar(Partida(), 3)
    p.abrir_bau(acertou=True)
    assert p.vidas_extras == 1 and not p.andar_tem_bau
    assert p.iniciar_duelo().vidas_jogador == 4


def test_errar_o_bau_nao_custa_nada_nem_da_coracao():
    p = _ir_para_o_andar(Partida(), 3)
    p.abrir_bau(acertou=False)
    assert p.vidas_extras == 0 and not p.andar_tem_bau
    assert p.iniciar_duelo().vidas_jogador == 3


def test_dois_baus_somam_5_coracoes_no_ultimo_andar():
    p = _ir_para_o_andar(Partida(), 3)
    p.abrir_bau(True)
    _ir_para_o_andar(p, 4).abrir_bau(True)
    assert p.vidas_iniciais == 5 and p.iniciar_duelo().vidas_jogador == 5


def test_estrelas_continuam_no_maximo_3_com_mais_de_3_coracoes():
    assert estrelas_por_vidas(5) == 3 and estrelas_por_vidas(4) == 3


def test_game_over_perde_os_coracoes_dos_baus_e_reabre_os_baus():
    p = _ir_para_o_andar(Partida(), 3)
    p.abrir_bau(True)
    p.iniciar_duelo()
    for _ in range(p.vidas_iniciais):
        p.duelo.responder((p.duelo.pergunta_atual["correta"] + 1) % len(p.duelo.pergunta_atual["opcoes"]))
        if not p.duelo.terminou:
            p.duelo.proxima_pergunta()
    assert p.concluir_duelo() == GAME_OVER
    assert p.vidas_extras == 0 and p.andar_atual == 1 and not p.baus_abertos


def test_pergunta_do_bau_respeita_o_nivel_do_andar_e_nao_repete():
    p = _ir_para_o_andar(Partida(), 3)
    sorteadas = [p.sortear_pergunta_bau() for _ in range(6)]       # há 6 fáceis/médias: nenhuma repete
    assert {q["nivel"] for q in sorteadas} <= {1, 2}
    assert len({q["id"] for q in sorteadas}) == 6
    p4 = _ir_para_o_andar(Partida(), 4)
    assert {p4.sortear_pergunta_bau()["nivel"] for _ in range(3)} <= {2, 3}
    for q in sorteadas:
        assert 0 <= q["correta"] < len(q["opcoes"])


def test_pergunta_do_bau_com_banco_vazio_levanta_erro():
    with pytest.raises(RuntimeError, match="vazio"):
        _ir_para_o_andar(Partida(), 3).sortear_pergunta_bau(banco=[])
