"""Testes da parte de interface que não precisa de janela: quebra de linha e fonte."""
import pygame
import pytest

from config.config import FONTE_PADRAO, FONTES_DIR
from src.telas import quebrar_texto


class FonteFalsa:
    """Cada caractere mede 10 pixels."""
    def size(self, texto):
        return (len(texto) * 10, 20)


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
