"""Testes da parte de interface que não precisa de janela: quebra de linha, fonte, golpe e game over.
(As telas que carregam imagens usam uma janela "dummy": nada aparece na tela.)"""
import math
import os
from collections import defaultdict

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
import pytest

from config.config import FONTE_PADRAO, FONTES_DIR
from src.regras import Duelo
from src import telas
from src.telas import TelaDuelo, TelaExploracao, TelaGameOver, curva_golpe, quebrar_texto


class FonteFalsa:
    """Cada caractere mede 10 pixels."""
    def size(self, texto):
        return (len(texto) * 10, 20)


def tecla(k):
    return pygame.event.Event(pygame.KEYDOWN, key=k)


@pytest.fixture
def janela():
    pygame.display.init()
    pygame.font.init()
    pygame.display.set_mode((1280, 720))


def test_quebrar_texto_curto_fica_em_uma_linha():
    assert quebrar_texto("Simplifique ¬(¬p).", FonteFalsa(), 1000) == ["Simplifique ¬(¬p)."]


def test_quebrar_texto_quebra_nos_espacos_sem_passar_da_largura():
    linhas = quebrar_texto("aaa bbb ccc ddd", FonteFalsa(), 80)  # cabem 8 caracteres
    assert linhas == ["aaa bbb", "ccc ddd"]
    assert all(FonteFalsa().size(l)[0] <= 80 for l in linhas)


def test_quebrar_texto_corta_palavra_maior_que_a_caixa():
    linhas = quebrar_texto("abcdefghijkl", FonteFalsa(), 50)  # cabem 5 caracteres
    assert "".join(linhas) == "abcdefghijkl"
    assert all(len(l) <= 5 for l in linhas)


def test_quebrar_texto_vazio():
    assert quebrar_texto("", FonteFalsa(), 100) == []


def test_fonte_tem_os_simbolos_logicos():
    pygame.font.init()
    fonte = pygame.font.Font(FONTES_DIR / FONTE_PADRAO, 24)
    for simbolo in "∧∨¬→↔≡":
        assert fonte.metrics(simbolo)[0] is not None, f"a fonte não tem {simbolo}"


# --- Exploração: W, A, S, D e setas ---

def teclado(*teclas):
    """Simula as teclas seguradas (o mesmo que pygame.key.get_pressed())."""
    return defaultdict(bool, {t: True for t in teclas})


def _andar(tela, teclas, segundos, passo=1 / 60):
    for _ in range(round(segundos / passo)):
        tela.atualizar(passo, teclas)


def test_sem_teclas_o_exterminador_fica_parado(janela):
    tela = TelaExploracao()
    x, y = tela.x, tela.y
    _andar(tela, teclado(), 1.0)
    assert (tela.x, tela.y) == (x, y) and not tela.andando


@pytest.mark.parametrize("tecla_frente", [pygame.K_w, pygame.K_UP])
def test_w_e_seta_para_cima_avancam(janela, tecla_frente):
    tela = TelaExploracao()
    y0 = tela.y
    _andar(tela, teclado(tecla_frente), 0.5)
    assert tela.y < y0 and tela.andando


@pytest.mark.parametrize("tecla, sinal", [(pygame.K_d, 1), (pygame.K_RIGHT, 1), (pygame.K_a, -1), (pygame.K_LEFT, -1)])
def test_a_d_e_setas_andam_de_lado(janela, tecla, sinal):
    tela = TelaExploracao()
    x0, y0 = tela.x, tela.y
    _andar(tela, teclado(tecla), 0.3)
    assert (tela.x - x0) * sinal > 0 and tela.y == y0


@pytest.mark.parametrize("tecla_tras", [pygame.K_s, pygame.K_DOWN])
def test_s_e_seta_para_baixo_voltam_mas_nao_saem_do_inicio(janela, tecla_tras):
    tela = TelaExploracao()
    _andar(tela, teclado(pygame.K_w), 0.5)
    y_meio = tela.y
    _andar(tela, teclado(tecla_tras), 0.2)
    assert tela.y > y_meio
    _andar(tela, teclado(tecla_tras), 5.0)
    assert tela.y == telas.CENAS[0]["y"][0]          # não passa do início do caminho


def test_nao_sai_do_caminho_para_os_lados(janela):
    tela = TelaExploracao()
    _andar(tela, teclado(pygame.K_a), 10.0)
    assert tela.x == telas.CENAS[0]["x_ini"][0]
    _andar(tela, teclado(pygame.K_d), 10.0)
    assert tela.x == telas.CENAS[0]["x_ini"][1]


def test_na_diagonal_nao_anda_mais_rapido(janela):
    reto, diag = TelaExploracao(), TelaExploracao()
    y0 = reto.y
    _andar(reto, teclado(pygame.K_w), 0.2)
    _andar(diag, teclado(pygame.K_w, pygame.K_d), 0.2)
    # Com duas teclas, cada direção anda 0,707 do que andaria sozinha.
    assert (y0 - diag.y) == pytest.approx((y0 - reto.y) * math.sqrt(0.5), rel=0.01)
    assert diag.x > reto.x


def test_encolhe_ao_se_afastar_pela_perspectiva(janela):
    tela = TelaExploracao()
    perto = tela._escala_bruta()
    _andar(tela, teclado(pygame.K_w), 1.5)
    assert tela._escala_bruta() < perto


def test_chegar_ao_fim_da_cena_leva_a_proxima_e_depois_ao_chefe(janela):
    tela = TelaExploracao()
    cenas_vistas = [tela.cena]
    for _ in range(round(30 * 60)):  # segurando W, no máximo 30 s
        tela.atualizar(1 / 60, teclado(pygame.K_w))
        if tela.cena != cenas_vistas[-1]:
            cenas_vistas.append(tela.cena)
        if tela.concluida:
            break
    assert cenas_vistas == [0, 1, 2]                 # porta, salão e escada, em ordem
    assert tela.concluida                            # encontro com o chefe


def test_nao_troca_de_cena_antes_de_chegar_ao_fim(janela):
    tela = TelaExploracao()
    _andar(tela, teclado(pygame.K_w), telas.CENAS[0]["tempo"] * 0.5)
    assert tela.cena == 0 and tela.fade_saida is None


def test_enter_pula_a_exploracao(janela):
    tela = TelaExploracao()
    tela.tratar_evento(tecla(pygame.K_RETURN))
    assert tela.concluida


def test_exploracao_desenha_sem_erro_andando_e_parado(janela):
    tela = TelaExploracao()
    alvo = pygame.display.get_surface()
    tela.desenhar(alvo)
    for _ in range(30):
        tela.atualizar(1 / 60, teclado(pygame.K_w, pygame.K_d))
        tela.desenhar(alvo)


# --- Golpe ---

def test_golpe_comeca_e_termina_em_pe_na_origem():
    assert curva_golpe(0.0) == (0.0, 0.0)
    avanco, inclinacao = curva_golpe(1.0)
    assert avanco == pytest.approx(0.0) and inclinacao == pytest.approx(0.0)


def test_golpe_chega_perto_do_alvo_e_se_inclina():
    avanco, inclinacao = curva_golpe(0.45)
    assert avanco == pytest.approx(1.0)
    assert inclinacao == pytest.approx(1.0)


def test_golpe_se_prepara_para_tras_antes_de_atacar():
    assert curva_golpe(0.15)[1] < 0


# --- Tela do duelo: golpe, painel e corações ---

def _avancar(tela, segundos, passo=1 / 60):
    for _ in range(round(segundos / passo)):
        tela.atualizar(passo)


def _responder(tela, certo):
    p = tela.duelo.pergunta_atual
    escolha = p["correta"] if certo else (p["correta"] + 1) % len(p["opcoes"])
    tela.tratar_evento(tecla(pygame.K_1 + escolha))
    tela.tratar_evento(tecla(pygame.K_RETURN))


def test_fases_do_acerto_e_coracao_do_chefe_so_some_no_golpe(janela):
    tela = TelaDuelo(Duelo(1))
    assert tela.fase == telas.FASE_PERGUNTA and tela.vidas_chefe_ex == 3
    _responder(tela, certo=True)
    assert tela.fase == telas.FASE_PISCADA
    assert tela.vidas_chefe_ex == 3                      # ainda não houve golpe
    assert tela.duelo.vidas_chefe == 2                   # mas o dano já foi decidido em regras.py

    _avancar(tela, telas.FLASH_TEMPO + 0.05)
    assert tela.fase == telas.FASE_ATAQUE
    assert tela.vidas_chefe_ex == 3                      # a espada ainda não acertou
    _avancar(tela, telas.GOLPE_INICIO + telas.GOLPE_IMPACTO * telas.GOLPE_DURACAO + 0.05)
    assert tela.vidas_chefe_ex == 2                      # o coração some no impacto
    assert tela.vidas_jogador_ex == 3

    _avancar(tela, telas.ATAQUE_TEMPO)
    assert tela.fase == telas.FASE_RESULTADO


def test_no_erro_quem_ataca_e_o_chefe_e_o_coracao_do_jogador_some(janela):
    tela = TelaDuelo(Duelo(1))
    _responder(tela, certo=False)
    _avancar(tela, telas.FLASH_TEMPO + 0.05)
    (dx_j, _, _), (dx_c, ang_c, _) = tela._poses()
    assert dx_c <= 0                                     # o chefe avança para a esquerda
    _avancar(tela, telas.ATAQUE_TEMPO)
    assert tela.vidas_jogador_ex == 2 == tela.duelo.vidas_jogador
    assert tela.vidas_chefe_ex == 3


def test_a_pergunta_sai_da_tela_durante_o_golpe_e_volta_depois(janela):
    tela = TelaDuelo(Duelo(1))
    _responder(tela, certo=True)
    assert tela._deslocamento_painel() == 0
    _avancar(tela, telas.FLASH_TEMPO + 0.05)
    _avancar(tela, telas.PAINEL_TRANSICAO + 0.1)
    assert tela._deslocamento_painel() == -(telas.PAINEL.bottom + 10)   # fora da tela
    _avancar(tela, telas.ATAQUE_TEMPO)
    assert tela.fase == telas.FASE_RESULTADO
    assert tela._deslocamento_painel() == 0


def test_quem_leva_o_golpe_pisca_vermelho_e_e_empurrado(janela):
    tela = TelaDuelo(Duelo(1))
    _responder(tela, certo=True)                        # o Exterminador ataca; o chefe leva dano
    _avancar(tela, telas.FLASH_TEMPO + 0.05)
    _avancar(tela, telas.GOLPE_INICIO + telas.GOLPE_IMPACTO * telas.GOLPE_DURACAO + 0.02)
    (_, _, jogador_pisca), (dx_chefe, _, chefe_pisca) = tela._poses()
    assert chefe_pisca is True and jogador_pisca is False
    assert dx_chefe >= 0                                 # empurrado para longe do Exterminador
    tela.desenhar(pygame.display.get_surface())          # desenhar com a piscada não pode dar erro


def test_enter_so_continua_na_tela_de_resultado(janela):
    tela = TelaDuelo(Duelo(1))
    _responder(tela, certo=True)
    tela.tratar_evento(tecla(pygame.K_RETURN))
    assert tela.fase == telas.FASE_PISCADA               # ignorado durante a piscada
    _avancar(tela, telas.FLASH_TEMPO + 0.05)
    tela.tratar_evento(tecla(pygame.K_RETURN))
    assert tela.fase == telas.FASE_ATAQUE                # ignorado durante o golpe
    _avancar(tela, telas.ATAQUE_TEMPO)
    _avancar(tela, telas.ESPERA_MINIMA + 0.05)
    tela.tratar_evento(tecla(pygame.K_RETURN))
    assert tela.fase == telas.FASE_PERGUNTA              # agora continua


def test_ultimo_golpe_do_jogador_leva_ao_fim_do_duelo(janela):
    duelo = Duelo(1, vidas_jogador=1)
    tela = TelaDuelo(duelo)
    _responder(tela, certo=False)
    _avancar(tela, telas.FLASH_TEMPO + telas.ATAQUE_TEMPO + telas.ESPERA_MINIMA + 0.1)
    assert tela.fase == telas.FASE_RESULTADO and tela.vidas_jogador_ex == 0
    tela.tratar_evento(tecla(pygame.K_RETURN))
    assert tela.concluida and duelo.game_over


def test_todas_as_fases_desenham_sem_erro(janela):
    tela = TelaDuelo(Duelo(1))
    alvo = pygame.display.get_surface()
    tela.desenhar(alvo)
    _responder(tela, certo=False)
    for _ in range(round((telas.FLASH_TEMPO + telas.ATAQUE_TEMPO + 0.5) * 60)):
        tela.atualizar(1 / 60)
        tela.desenhar(alvo)


# --- Game Over ---

def test_game_over_so_mostra_a_mensagem_depois_de_2_segundos(janela):
    tela = TelaGameOver()
    assert not tela.mensagem_visivel
    tela.atualizar(1.9)
    assert not tela.mensagem_visivel
    tela.atualizar(0.2)
    assert tela.mensagem_visivel


def test_game_over_ignora_enter_antes_da_mensagem_e_volta_ao_menu_depois(janela):
    tela = TelaGameOver()
    tela.atualizar(1.0)
    tela.tratar_evento(tecla(pygame.K_RETURN))
    assert not tela.concluida
    tela.atualizar(1.5)
    tela.tratar_evento(tecla(pygame.K_RETURN))
    assert tela.concluida and tela.acao == "menu"


def test_game_over_desenha_preto_com_letras_vermelhas(janela):
    tela = TelaGameOver()
    alvo = pygame.display.get_surface()
    tela.desenhar(alvo)
    assert alvo.get_at((5, 5))[:3] == (0, 0, 0)            # fundo totalmente preto
    vermelho = [alvo.get_at((x, 360))[:3] for x in range(300, 980)]
    assert any(r > 150 and g < 60 and b < 60 for r, g, b in vermelho)   # letras vermelhas no centro
    assert alvo.get_at((1200, 700))[:3] == (0, 0, 0)       # sem mensagem ainda no canto inferior direito
    tela.atualizar(2.1)
    tela.desenhar(alvo)
    canto = [alvo.get_at((x, y))[:3] for x in range(900, 1250) for y in range(660, 700)]
    assert any(c != (0, 0, 0) for c in canto)              # mensagem apareceu no canto inferior direito
