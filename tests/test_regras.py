import pytest
from src.regras import carregar_perguntas, verificar_resposta


def test_perguntas_validas():
    quantidades = {1: 6, 2: 8, 3: 8, 4: 10}
    for andar, qtd in quantidades.items():
        perguntas = carregar_perguntas(andar)
        assert len(perguntas) == qtd
        for p in perguntas:
            assert 0 <= p["correta"] < len(p["opcoes"])


def test_verificar_resposta():
    p = {"correta": 2}
    assert verificar_resposta(p, 2)
    assert not verificar_resposta(p, 0)