"""Testes da parte de interface que não precisa de janela: quebra de linha, fonte, golpe e game over.
(As telas que carregam imagens usam uma janela "dummy": nada aparece na tela.)"""
import math
import os
from collections import defaultdict

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")   # os testes não tocam som de verdade

import pygame
import pytest

from config.config import COR_OURO, FONTE_PADRAO, FONTES_DIR, SONS_DIR
from src import recursos
from src.regras import Duelo
from src import telas
from src.tela_conclusao import TelaConclusao
from src.telas import (
    TelaAndarConcluido, TelaDuelo, TelaExploracao, TelaGameOver, TelaPausa, curva_golpe, desenhar_estrela, quebrar_texto,
)


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


def test_enter_e_espaco_nao_pulam_a_exploracao(janela):
    tela = TelaExploracao()
    tela.tratar_evento(tecla(pygame.K_RETURN))
    tela.tratar_evento(tecla(pygame.K_SPACE))
    assert not tela.concluida


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
    tela.tratar_evento(tecla(pygame.K_RETURN))   # abre "Confirmar a resposta?"
    tela.tratar_evento(tecla(pygame.K_RETURN))   # Enter em "Confirmar"


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


def test_game_over_tambem_volta_ao_menu_com_clique(janela):
    tela = TelaGameOver()
    clique = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(100, 100))
    tela.tratar_evento(clique)
    assert not tela.concluida                              # a mensagem ainda não apareceu
    tela.atualizar(2.1)
    tela.tratar_evento(clique)
    assert tela.concluida and tela.acao == "menu"


# --- Mouse na tela de pergunta (além do teclado) ---

def _centro_da_opcao(tela, i):
    rect = tela._retangulos_opcoes(tela.duelo.pergunta_atual)[i]
    return rect.move(telas.PAINEL.x, telas.PAINEL.y).center


def test_passar_o_mouse_seleciona_a_alternativa(janela):
    tela = TelaDuelo(Duelo(1))
    tela.tratar_evento(pygame.event.Event(pygame.MOUSEMOTION, pos=_centro_da_opcao(tela, 2), rel=(0, 0), buttons=(0, 0, 0)))
    assert tela.selecionada == 2 and tela.fase == telas.FASE_PERGUNTA   # só destaca, não responde


def _centro_do_botao(tela, i):
    rect = tela._botoes_confirmacao(tela.duelo.pergunta_atual)[i]
    return rect.move(telas.PAINEL.x, telas.PAINEL.y).center


def test_clicar_na_alternativa_escolhe_e_confirma(janela):
    tela = TelaDuelo(Duelo(1))
    correta = tela.duelo.pergunta_atual["correta"]
    tela.tratar_evento(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=_centro_da_opcao(tela, correta)))
    assert tela.fase == telas.FASE_PERGUNTA and tela.confirmando      # o clique só pergunta
    tela.tratar_evento(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=_centro_do_botao(tela, 0)))
    assert tela.fase == telas.FASE_PISCADA and tela.escolhida == correta
    assert tela.duelo.ultimo_acertou is True and tela.duelo.vidas_chefe == 2


def test_clicar_fora_das_alternativas_nao_faz_nada(janela):
    tela = TelaDuelo(Duelo(1))
    tela.tratar_evento(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(5, 5)))
    assert tela.fase == telas.FASE_PERGUNTA and tela.escolhida is None


def test_botao_direito_nao_responde(janela):
    tela = TelaDuelo(Duelo(1))
    tela.tratar_evento(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=3, pos=_centro_da_opcao(tela, 0)))
    assert tela.fase == telas.FASE_PERGUNTA


def test_clique_na_tela_de_resultado_continua(janela):
    tela = TelaDuelo(Duelo(1))
    _responder(tela, certo=True)
    _avancar(tela, telas.FLASH_TEMPO + telas.ATAQUE_TEMPO + telas.ESPERA_MINIMA + 0.1)
    assert tela.fase == telas.FASE_RESULTADO
    tela.tratar_evento(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(640, 360)))
    assert tela.fase == telas.FASE_PERGUNTA


def test_teclado_continua_funcionando_junto_com_o_mouse(janela):
    tela = TelaDuelo(Duelo(1))
    tela.tratar_evento(tecla(pygame.K_DOWN))
    assert tela.selecionada == 1
    tela.tratar_evento(tecla(pygame.K_3))
    assert tela.selecionada == 2
    tela.tratar_evento(tecla(pygame.K_RETURN))
    tela.tratar_evento(tecla(pygame.K_RETURN))
    assert tela.fase == telas.FASE_PISCADA


# --- Estrelas e tela de andar concluído ---

def test_estrela_preenchida_e_dourada_e_a_vazia_nao(janela):
    alvo = pygame.display.get_surface()
    alvo.fill((0, 0, 0))
    desenhar_estrela(alvo, (100, 100), 40, True)
    desenhar_estrela(alvo, (300, 100), 40, False)
    assert alvo.get_at((100, 100))[:3] == COR_OURO
    assert alvo.get_at((300, 100))[:3] != COR_OURO


def _tela_andar(pode_repetir=True, estrelas=1, melhor=1):
    tela = TelaAndarConcluido(1, estrelas, melhor, pode_repetir)
    tela.atualizar(telas.ANDAR_CONCLUIDO_ESPERA + 0.1)
    return tela


def test_andar_concluido_comeca_em_continuar_para_nao_repetir_sem_querer(janela):
    tela = _tela_andar()
    assert tela.acoes == ["repetir", "continuar"]
    tela.tratar_evento(tecla(pygame.K_RETURN))
    assert tela.concluida and tela.acao == "continuar"


def test_andar_concluido_escolhe_repetir_com_setas_ou_numero(janela):
    for teclas in ([pygame.K_UP], [pygame.K_LEFT], [pygame.K_1]):
        tela = _tela_andar()
        for t in teclas:
            tela.tratar_evento(tecla(t))
        tela.tratar_evento(tecla(pygame.K_RETURN))
        assert tela.acao == "repetir", teclas


def test_com_3_estrelas_so_ha_a_opcao_continuar(janela):
    tela = _tela_andar(pode_repetir=False, estrelas=3, melhor=3)
    assert tela.acoes == ["continuar"]
    tela.tratar_evento(tecla(pygame.K_UP))
    tela.tratar_evento(tecla(pygame.K_RETURN))
    assert tela.acao == "continuar"


def test_andar_concluido_ignora_teclas_no_primeiro_instante(janela):
    tela = TelaAndarConcluido(1, 1, 1, True)
    tela.tratar_evento(tecla(pygame.K_RETURN))
    assert not tela.concluida


def test_andar_concluido_com_mouse(janela):
    tela = _tela_andar()
    centro_repetir = tela._retangulo_opcao(0).center
    tela.tratar_evento(pygame.event.Event(pygame.MOUSEMOTION, pos=centro_repetir, rel=(0, 0), buttons=(0, 0, 0)))
    assert tela.selecionada == 0 and not tela.concluida     # passar o mouse só destaca
    tela.tratar_evento(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=centro_repetir))
    assert tela.concluida and tela.acao == "repetir"


@pytest.mark.parametrize("andar", [1, 2, 3, 4])
def test_andar_concluido_desenha_em_todos_os_andares(janela, andar):
    TelaAndarConcluido(andar, 2, 3, False).desenhar(pygame.display.get_surface())
    _tela_andar().desenhar(pygame.display.get_surface())


# --- Vitória ---

def test_vitoria_mostra_a_pontuacao_e_so_volta_ao_menu_depois_da_mensagem(janela):
    tela = TelaConclusao(pontuacao=9)
    tela.tratar_evento(tecla(pygame.K_RETURN))
    assert not tela.concluida
    tela.atualizar(20.0)
    tela.desenhar(pygame.display.get_surface())
    tela.tratar_evento(tecla(pygame.K_RETURN))
    assert tela.concluida and tela.acao == "menu"


def test_vitoria_tambem_volta_ao_menu_com_clique(janela):
    tela = TelaConclusao(pontuacao=12)
    tela.atualizar(20.0)
    tela.tratar_evento(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(10, 10)))
    assert tela.concluida


def test_vitoria_funciona_sem_pontuacao(janela):
    TelaConclusao().desenhar(pygame.display.get_surface())


# --- Exploração dos 4 andares ---

@pytest.mark.parametrize("andar", [1, 2, 3, 4])
def test_exploracao_de_cada_andar_leva_ao_chefe(janela, andar):
    tela = TelaExploracao(andar)
    cenas = [tela.cena]
    for _ in range(round(40 * 60)):
        tela.atualizar(1 / 60, teclado(pygame.K_w))
        if tela.cena != cenas[-1]:
            cenas.append(tela.cena)
        if tela.concluida:
            break
    assert tela.concluida
    assert len(cenas) == len(telas.CENAS_POR_ANDAR[andar])


# --- Sons ---

@pytest.mark.parametrize("nome", [recursos.SOM_ACERTO, recursos.SOM_ERRO, recursos.SOM_VITORIA, recursos.SOM_GAME_OVER, *recursos.SOM_PASSOS])
def test_os_sons_existem_e_carregam(nome):
    assert (SONS_DIR / nome).exists()
    pygame.mixer.init()
    assert pygame.mixer.Sound(SONS_DIR / nome).get_length() > 0.1


def test_tocar_som_nao_quebra_se_o_arquivo_nao_existir():
    recursos.tocar_som("nao_existe.wav")        # só avisa no terminal, não levanta erro
    recursos.tocar_som(recursos.SOM_ACERTO)


def test_passos_tocam_so_enquanto_anda_e_no_ritmo_da_animacao(janela, monkeypatch):
    tocados = []
    monkeypatch.setattr(telas, "tocar_som", tocados.append)
    tela = TelaExploracao(1)
    parado = defaultdict(bool)
    andando = defaultdict(bool, {pygame.K_w: True})
    tela.atualizar(0.5, parado)
    assert tocados == []                                 # parado: sem passos
    for _ in range(10):
        tela.atualizar(0.1, andando)                     # 1 s andando
    assert set(tocados) <= set(recursos.SOM_PASSOS) and len(set(tocados)) > 1   # alterna as variações
    assert 3 <= len(tocados) <= 5                        # ~3,2 passos por segundo (+ o primeiro)
    tocados.clear()
    tela.atualizar(0.1, parado)
    assert tocados == []


def test_responder_toca_o_som_certo(janela, monkeypatch):
    tocados = []
    monkeypatch.setattr(telas, "tocar_som", tocados.append)
    tela = TelaDuelo(Duelo(1))
    _responder(tela, certo=True)
    tela2 = TelaDuelo(Duelo(1))
    _responder(tela2, certo=False)
    assert tocados == [recursos.SOM_ACERTO, recursos.SOM_ERRO]


# --- Pausa (ESC), dicas na tela e explicação no acerto ---

def _tecla(k):
    return pygame.event.Event(pygame.KEYDOWN, key=k)


def test_pausa_escolhe_com_teclado_e_esc_continua(janela):
    p = TelaPausa()
    assert p.tratar_evento(_tecla(pygame.K_ESCAPE)) == "continuar"
    assert p.tratar_evento(_tecla(pygame.K_DOWN)) is None and p.selecionada == 1
    assert p.tratar_evento(_tecla(pygame.K_RETURN)) == "som"
    assert p.tratar_evento(_tecla(pygame.K_UP)) is None and p.selecionada == 0
    assert p.tratar_evento(_tecla(pygame.K_3)) == "menu"
    assert p.tratar_evento(_tecla(pygame.K_4)) == "sair"


def test_pausa_com_mouse_e_desenha(janela):
    p = TelaPausa()
    alvo = p._retangulo_opcao(2).center
    assert p.tratar_evento(pygame.event.Event(pygame.MOUSEMOTION, pos=alvo, rel=(0, 0), buttons=(0, 0, 0))) is None
    assert p.selecionada == 2
    assert p.tratar_evento(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=alvo, button=1)) == "menu"
    p.desenhar(pygame.display.get_surface())


def test_alternar_mudo_silencia_os_sons(monkeypatch):
    tocados = []
    monkeypatch.setattr(recursos, "_iniciar_audio", lambda: tocados.append("iniciou") or True)
    assert recursos.som_mudo() is False
    try:
        assert recursos.alternar_mudo() is True
        recursos.tocar_som(recursos.SOM_ACERTO)
        assert tocados == []                      # mudo: nem tenta tocar
        assert TelaPausa().rotulo("som") == "Som: desligado"
    finally:
        if recursos.som_mudo():
            recursos.alternar_mudo()
    assert TelaPausa().rotulo("som") == "Som: ligado"


def test_dicas_de_controle_desenham_na_exploracao_e_no_duelo(janela):
    tela = pygame.display.get_surface()
    expl = TelaExploracao(1)
    expl.atualizar(0.1, defaultdict(bool))
    expl.desenhar(tela)
    expl.tempo_cena = telas.DICA_TEMPO + telas.DICA_FADE + 1   # depois de sumir, continua desenhando sem erro
    expl.desenhar(tela)
    TelaDuelo(Duelo(1)).desenhar(tela)


def test_explicacao_aparece_tambem_no_acerto(janela, monkeypatch):
    desenhados = []
    original = telas._linhas
    monkeypatch.setattr(telas, "_linhas", lambda *a, **k: desenhados.append(a[1]) or original(*a, **k))
    tela = TelaDuelo(Duelo(1))
    tela.selecionada = tela.duelo.pergunta_atual["correta"]
    tela._confirmar()
    tela.fase = telas.FASE_RESULTADO
    tela.tempo_fase = 1.0
    tela.desenhar(pygame.display.get_surface())
    assert tela.duelo.ultimo_acertou
    assert any(tela.duelo.explicacao[:15] in " ".join(linhas) for linhas in desenhados)


# --- Confirmar ou cancelar a resposta ---

def test_enter_na_alternativa_so_pergunta_e_nada_vale_ainda(janela):
    tela = TelaDuelo(Duelo(1))
    vidas = (tela.duelo.vidas_jogador, tela.duelo.vidas_chefe)
    tela.tratar_evento(tecla(pygame.K_2))
    tela.tratar_evento(tecla(pygame.K_RETURN))
    assert tela.confirmando and tela.foco_confirmar == 0       # já começa em "Confirmar"
    assert tela.fase == telas.FASE_PERGUNTA and tela.escolhida is None
    assert (tela.duelo.vidas_jogador, tela.duelo.vidas_chefe) == vidas
    tela.desenhar(pygame.display.get_surface())


def test_cancelar_volta_as_alternativas_sem_responder(janela):
    tela = TelaDuelo(Duelo(1))
    tela.tratar_evento(tecla(pygame.K_2))
    tela.tratar_evento(tecla(pygame.K_RETURN))
    tela.tratar_evento(tecla(pygame.K_RIGHT))
    assert tela.foco_confirmar == 1
    tela.tratar_evento(tecla(pygame.K_RETURN))                 # Enter em "Cancelar"
    assert not tela.confirmando and tela.fase == telas.FASE_PERGUNTA and tela.escolhida is None
    assert tela.selecionada == 1                               # a alternativa continua marcada
    tela.tratar_evento(tecla(pygame.K_RETURN))
    tela.tratar_evento(tecla(pygame.K_BACKSPACE))              # Backspace também cancela
    assert not tela.confirmando and tela.escolhida is None


def test_cancelar_com_o_mouse_e_trocar_de_alternativa_desfaz_a_pergunta(janela):
    tela = TelaDuelo(Duelo(1))
    tela.tratar_evento(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=_centro_da_opcao(tela, 1)))
    tela.tratar_evento(pygame.event.Event(pygame.MOUSEMOTION, pos=_centro_do_botao(tela, 1), rel=(0, 0), buttons=(0, 0, 0)))
    assert tela.foco_confirmar == 1
    tela.tratar_evento(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=_centro_do_botao(tela, 1)))
    assert not tela.confirmando and tela.escolhida is None
    tela.tratar_evento(tecla(pygame.K_RETURN))
    tela.tratar_evento(tecla(pygame.K_3))                      # outra alternativa: a pergunta some
    assert not tela.confirmando and tela.selecionada == 2


def test_clicar_fora_dos_botoes_enquanto_confirma_nao_responde(janela):
    tela = TelaDuelo(Duelo(1))
    tela.tratar_evento(tecla(pygame.K_RETURN))
    tela.tratar_evento(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=_centro_da_opcao(tela, 2)))
    assert tela.confirmando and tela.escolhida is None and tela.fase == telas.FASE_PERGUNTA


# --- Baú da exploração ---

def _levar_ao_bau(tela):
    tela.cena = telas.BAU_CENA
    tela.fade_entrada = 0.0
    tela.x, tela.y = float(telas.BAU_POS[0]), float(telas.BAU_POS[1])


def test_bau_so_aparece_perto_e_no_corredor_com_bau(janela):
    tela = TelaExploracao(3, com_bau=True)
    assert not tela.perto_do_bau                       # na escada ainda não
    _levar_ao_bau(tela)
    assert tela.perto_do_bau
    tela.x = telas.BAU_POS[0] - telas.BAU_ALCANCE[0] - 5
    assert not tela.perto_do_bau                       # longe demais
    _levar_ao_bau(tela)
    assert not TelaExploracao(2, com_bau=False).perto_do_bau
    tela.desenhar(pygame.display.get_surface())        # desenha o botão ABRIR sem erro


def test_enter_perto_do_bau_abre_e_nao_pula_a_exploracao(janela):
    tela = TelaExploracao(3, com_bau=True)
    _levar_ao_bau(tela)
    tela.tratar_evento(tecla(pygame.K_RETURN))
    assert tela.pedir_bau and not tela.concluida
    tela.pedir_bau = False
    tela.tratar_evento(tecla(pygame.K_SPACE))          # Espaço não faz nada
    assert not tela.pedir_bau and not tela.concluida


def test_clicar_em_abrir_pede_o_bau_e_clicar_fora_nao(janela):
    tela = TelaExploracao(3, com_bau=True)
    _levar_ao_bau(tela)
    tela.tratar_evento(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(5, 5)))
    assert not tela.pedir_bau
    tela.tratar_evento(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=tela._botao_abrir().center))
    assert tela.pedir_bau


def test_enter_longe_do_bau_nao_faz_nada(janela):
    tela = TelaExploracao(3, com_bau=True)
    tela.tratar_evento(tecla(pygame.K_RETURN))
    assert not tela.concluida and not tela.pedir_bau


def test_bau_resolvido_deixa_o_bau_aberto_e_mostra_a_mensagem(janela):
    tela = TelaExploracao(3, com_bau=True)
    _levar_ao_bau(tela)
    tela.bau_resolvido(True)
    assert tela.bau_aberto and not tela.perto_do_bau and tela.mensagem_bau[2] is True
    tela.desenhar(pygame.display.get_surface())
    tela.atualizar(telas.BAU_MENSAGEM_TEMPO + 0.1, defaultdict(bool))
    assert tela.mensagem_bau is None


PERGUNTA_BAU = {"id": 1, "enunciado": "Qual símbolo é a negação?", "opcoes": ["∧", "¬", "∨"], "correta": 1,
                "explicacao": "¬p lê-se não p."}


def test_tela_bau_acerto_e_resultado(janela):
    tela = telas.TelaBau(dict(PERGUNTA_BAU))
    tela.desenhar(pygame.display.get_surface())
    tela.tratar_evento(tecla(pygame.K_2))
    tela.tratar_evento(tecla(pygame.K_RETURN))
    assert tela.confirmando and not tela.respondida     # primeiro pergunta
    tela.desenhar(pygame.display.get_surface())
    tela.tratar_evento(tecla(pygame.K_RETURN))          # Enter em "Confirmar"
    assert tela.respondida and tela.acertou is True and not tela.concluida
    tela.tratar_evento(tecla(pygame.K_RETURN))         # cedo demais: ainda não fecha
    assert not tela.concluida
    tela.atualizar(telas.BAU_ESPERA + 0.1)
    tela.desenhar(pygame.display.get_surface())
    tela.tratar_evento(tecla(pygame.K_RETURN))
    assert tela.concluida


def test_tela_bau_erro_e_mouse(janela):
    tela = telas.TelaBau(dict(PERGUNTA_BAU))
    alvo = tela._retangulos_opcoes()[0].center
    tela.tratar_evento(pygame.event.Event(pygame.MOUSEMOTION, pos=alvo, rel=(0, 0), buttons=(0, 0, 0)))
    assert tela.selecionada == 0
    tela.tratar_evento(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=alvo))
    assert tela.confirmando and not tela.respondida
    confirmar = tela._botoes_confirmacao()[0].center
    tela.tratar_evento(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=confirmar))
    assert tela.respondida and tela.acertou is False
    tela.atualizar(1.0)
    tela.desenhar(pygame.display.get_surface())
    tela.tratar_evento(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(5, 5)))
    assert tela.concluida


def test_tela_bau_cancelar_volta_as_alternativas_sem_responder(janela):
    tela = telas.TelaBau(dict(PERGUNTA_BAU))
    tela.tratar_evento(tecla(pygame.K_RETURN))
    tela.tratar_evento(tecla(pygame.K_RIGHT))
    assert tela.foco_confirmar == 1
    tela.tratar_evento(tecla(pygame.K_RETURN))                    # Enter em "Cancelar"
    assert not tela.confirmando and not tela.respondida
    tela.tratar_evento(tecla(pygame.K_RETURN))
    tela.tratar_evento(tecla(pygame.K_BACKSPACE))                 # Backspace também cancela
    assert not tela.confirmando and not tela.respondida
    tela.tratar_evento(tecla(pygame.K_RETURN))
    tela.tratar_evento(tecla(pygame.K_3))                         # outra alternativa desfaz a pergunta
    assert not tela.confirmando and tela.selecionada == 2
    tela.tratar_evento(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=tela._retangulos_opcoes()[1].center))
    tela.tratar_evento(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(5, 5)))   # fora dos botões
    assert tela.confirmando and not tela.respondida
    tela.tratar_evento(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=tela._botoes_confirmacao()[1].center))
    assert not tela.confirmando and not tela.respondida


def test_botoes_do_bau_ficam_onde_sao_desenhados(janela):
    """A área de clique de Confirmar e Cancelar tem que ser a mesma que aparece na tela."""
    tela = telas.TelaBau(dict(PERGUNTA_BAU))
    tela.tratar_evento(tecla(pygame.K_RETURN))
    alvo = pygame.display.get_surface()
    tela.desenhar(alvo)
    for i, cor_esperada in ((0, telas.COR_SELECIONADA), (1, telas.COR_PAINEL)):
        rect = tela._botoes_confirmacao()[i]
        assert tuple(alvo.get_at((rect.x + 12, rect.y + 6)))[:3] == cor_esperada
