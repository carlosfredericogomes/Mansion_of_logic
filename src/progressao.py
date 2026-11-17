from dataclasses import dataclass

from src.chefes import(
    CUSTO_ACERTO, CUSTO_ERRO, JOGADOR_VIDAS, RESTAURAR_VIDAS_POR_ANDAR,TOTAL_ANDARES,obter_chefe, perguntas_necessarias
)
from src.questoes import baralho_perguuntas
from src.regras import Estado, Evento, proximo_estado, verificar_resposta

@dataclass

class resultado_resposta:
    acertou: bool
    pergunta: dict
    indice_escolhido: int
    indice_correto: int
    explicacao: str
    vidas_chefe: int
    vidas_jogador: int
    estado: Estado