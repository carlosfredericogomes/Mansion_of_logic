"""O jogo inteiro rodando pelo main.py, do menu ao fim, só com o teclado.

O relógio é falso (cada quadro vale 0,1 s) e um "robô" dá as teclas no lugar do jogador. Nenhuma janela
nem som de verdade: usa os drivers "dummy" do SDL."""
import os
from collections import defaultdict

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pytest

import main
from src import recursos
from src.chefes import CHEFES
from src.telas import (
    FASE_PERGUNTA, FASE_RESULTADO, TelaAndarConcluido, TelaDuelo, TelaExploracao, TelaGameOver,
)
from src.tela_conclusao import TelaConclusao

pytestmark = pytest.mark.filterwarnings("ignore:no fast renderer")   # aviso do driver de vídeo "dummy"

ENTER = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
SAIR = pygame.event.Event(pygame.QUIT)


class RelogioFalso:
    def tick(self, fps=0):
        return 100  # milissegundos: o main limita o dt a 0,1 s


def tecla(k):
    return pygame.event.Event(pygame.KEYDOWN, key=k)


def jogar_pelo_main(monkeypatch, planos, escolher_acao_do_andar=lambda tela: []):
    """Roda main.menu_inicial() até o jogo pedir para sair. Devolve a lista de telas que apareceram.

    planos: para cada duelo, o que o robô faz ('C' = acerta, 'E' = erra); depois do plano, acerta."""
    telas_vistas = []

    def registrar(classe):
        class Registrada(classe):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                telas_vistas.append(self)
        Registrada.__name__ = classe.__name__   # os testes conferem a ordem pelo nome da tela
        return Registrada

    for nome in ("TelaExploracao", "TelaDuelo", "TelaAndarConcluido", "TelaGameOver", "TelaConclusao"):
        monkeypatch.setattr(main, nome, registrar(getattr(main, nome)))
    monkeypatch.setattr(pygame.time, "Clock", RelogioFalso)
    monkeypatch.setattr(pygame.key, "get_pressed", lambda: defaultdict(bool, {pygame.K_w: True}))  # segura W

    estado = {"quadros": 0, "respostas": defaultdict(int)}

    def eventos():
        estado["quadros"] += 1
        assert estado["quadros"] < 20000, "o jogo travou: passou de 20000 quadros"
        if not telas_vistas:
            return [ENTER] if estado["quadros"] == 3 else []   # Enter no menu
        tela = telas_vistas[-1]
        if isinstance(tela, (TelaGameOver, TelaConclusao)):
            return [SAIR] if tela.concluida else [ENTER, tecla(pygame.K_SPACE)][:1]
        if isinstance(tela, TelaAndarConcluido):
            return escolher_acao_do_andar(tela) + [ENTER]
        if isinstance(tela, TelaDuelo) and not tela.concluida:
            if tela.fase == FASE_PERGUNTA:
                indice_duelo = sum(isinstance(t, TelaDuelo) for t in telas_vistas) - 1
                plano = planos[indice_duelo] if indice_duelo < len(planos) else ""
                n = estado["respostas"][indice_duelo]
                estado["respostas"][indice_duelo] += 1
                acao = plano[n] if n < len(plano) else "C"
                p = tela.duelo.pergunta_atual
                escolha = p["correta"] if acao == "C" else (p["correta"] + 1) % len(p["opcoes"])
                return [tecla(pygame.K_1 + escolha), ENTER]
            if tela.fase == FASE_RESULTADO:
                return [ENTER]
        return []

    monkeypatch.setattr(pygame.event, "get", eventos)
    try:
        main.menu_inicial()
    except SystemExit:
        pass
    finally:  # o main chamou pygame.quit(): limpa o que ficou guardado (fontes, imagens, sons) para os outros testes
        recursos._cache_fontes.clear()
        recursos._cache_imagens.clear()
        recursos._cache_sons.clear()
        recursos._mixer_ok = None
    return telas_vistas


def tipos(telas_vistas):
    return [type(t).__name__ for t in telas_vistas]


def test_partida_perfeita_do_andar_1_a_vitoria_com_12_estrelas(monkeypatch):
    telas_vistas = jogar_pelo_main(monkeypatch, planos=[])       # acerta tudo
    assert tipos(telas_vistas) == [
        "TelaExploracao", "TelaDuelo", "TelaAndarConcluido",     # andar 1
        "TelaExploracao", "TelaDuelo", "TelaAndarConcluido",     # andar 2
        "TelaExploracao", "TelaDuelo", "TelaAndarConcluido",     # andar 3
        "TelaExploracao", "TelaDuelo", "TelaAndarConcluido",     # andar 4
        "TelaConclusao",
    ]
    duelos = [t for t in telas_vistas if isinstance(t, TelaDuelo)]
    assert [d.duelo.andar for d in duelos] == [1, 2, 3, 4]
    assert all(d.duelo.venceu and d.duelo.vidas_jogador == 3 for d in duelos)
    assert [d.nome_chefe for d in duelos] == [CHEFES[a]["nome"] for a in (1, 2, 3, 4)]
    assert telas_vistas[-1].pontuacao == 12 and telas_vistas[-1].acao == "menu"


def test_nova_chance_depois_de_1_estrela_e_game_over_no_andar_3(monkeypatch):
    # Andar 1: erra 2 vezes e vence com 1 coração (1 estrela) e tenta de novo, perfeito (3 estrelas).
    # Andar 2: perfeito. Andar 3: erra 3 vezes e perde.
    planos = [list("EECCC"), list("CCC"), list("CCCC"), list("EEE")]
    escolher_repetir = lambda tela: [tecla(pygame.K_1)] if tela.acoes[0] == "repetir" else []
    telas_vistas = jogar_pelo_main(monkeypatch, planos, escolher_repetir)

    assert tipos(telas_vistas) == [
        "TelaExploracao", "TelaDuelo", "TelaAndarConcluido",     # andar 1: 1 estrela
        "TelaDuelo", "TelaAndarConcluido",                       # nova chance, sem exploração: 3 estrelas
        "TelaExploracao", "TelaDuelo", "TelaAndarConcluido",     # andar 2
        "TelaExploracao", "TelaDuelo", "TelaGameOver",           # andar 3: game over
    ]
    duelo1, nova_chance, duelo2, duelo3 = [t for t in telas_vistas if isinstance(t, TelaDuelo)]
    assert duelo1.duelo.andar == nova_chance.duelo.andar == 1
    assert nova_chance.duelo.vidas_jogador == 3 and nova_chance.duelo.vidas_chefe == 0 and nova_chance.duelo.venceu

    primeiro_andar, segundo_andar, _ = [t for t in telas_vistas if isinstance(t, TelaAndarConcluido)]
    assert (primeiro_andar.estrelas, primeiro_andar.acoes) == (1, ["repetir", "continuar"])
    assert (segundo_andar.estrelas, segundo_andar.melhor, segundo_andar.acoes) == (3, 3, ["continuar"])
    assert duelo3.duelo.game_over and duelo3.duelo.vidas_jogador == 0
    assert telas_vistas[-1].acao == "menu"


def test_game_over_logo_no_andar_1(monkeypatch):
    telas_vistas = jogar_pelo_main(monkeypatch, planos=[list("EEE")])
    assert tipos(telas_vistas) == ["TelaExploracao", "TelaDuelo", "TelaGameOver"]
    assert telas_vistas[1].duelo.andar == 1
