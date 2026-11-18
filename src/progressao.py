from dataclasses import dataclass

from src.chefes import(
    CUSTO_ACERTO, CUSTO_ERRO, JOGADOR_VIDAS, RESTAURAR_VIDAS_POR_ANDAR,TOTAL_ANDARES,obter_chefe, perguntas_necessarias
)
from src.questoes import baralho_perguntas, carregar_perguntas, problemas_das_perguntas
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

class duelo: 
    def __init__(self, andar, vida_jogador=JOGADOR_VIDAS, perguntas=None, rng=None):
        self.andar = andar
        self.chefe = obter_chefe(andar)
        self.vidas_chefe = self.chefe["vidas"]
        self.vidas_jogador = vida_jogador
        if perguntas is None:
            perguntas = carregar_perguntas(andar)
        self.baralho = baralho_perguntas(perguntas, rng=rng)
        self.historico = []
        self.estado = proximo_estado(Estado.S0_EXPLORACAO, Evento.ENCONTRO_CHEFE) 
        self.pergunta_atual = self.baralho.proxima()

    def responder(self, indice_escolhido):
        if self.estado != self.estado.S1_PERGUNTA:
            raise RuntimeError(f"o duelo nao esta esperando resposta(estado{self.estado.name})")

        pergunta = self.pergunta_atual
        self.estado = proximo_estado(self.estado, Evento.CONFIRMOU_RESPOSTA)
        acertou = verificar_resposta(pergunta, indice_escolhido)

        if acertou:
            self.estado = proximo_estado(self.estado, Evento.ACERTOU)
            self.vidas_chefe = max(0, self.vidas_chefe - CUSTO_ACERTO)
            evento = Evento.CHEFE_SEM_VIDAS if self.vidas_chefe == 0 else Evento.CHEFE_COM_VIDAS

        else: 
            self. estado = proximo_estado(self.estado, Evento.ERROU)
            self.vidas_jogador = max(0, self.vidas_jogador - CUSTO_ERRO)
            evento = Evento.JOGADOR_SEM_VIDAS if self.vidas_jogador == 0 else Evento.JOGADOR_COM_VIDAS
        self.estado = proximo_estado(self.estado, evento)

        resultado = resultado_resposta(
            acertou=acertou,
            pergunta=pergunta,
            indice_escolhido=indice_escolhido,
            indice_correto=pergunta["correta"],
            explicacao=pergunta["explicacao"],
            vidas_chefe=self.vidas_chefe,
            vidas_jogador=self.vidas_jogador,
            estado=self.estado,
        )
        self.historico.append(resultado)

        self.pergunta_atual = self.baralho.proxima() if self.estado ==  Estado.S1_PERGUNTA else None
        return resultado

    @property
    def vitoria(self):
        return self.estado == Estado.S5_AVANCO_ANDAR

    @property
    def derrota(self):
        return self.estado == Estado.S6_GAME_OVER

    @property
    def terminado(self):
        return self.vitoria or self.derrota

class Partida:
    def __init__(self, carregador=carregar_perguntas, rng=None):
        self.carregador = carregador
        self.rng = rng
        self.andar_atual = 1
        self.vidas_jogador = JOGADOR_VIDAS
        self.duelo = None
        self.chefes_derrotados = []
        self.venceu_jogo = False

    @property
    def chefe_atual(self):
        return obter_chefe(self.andar_atual)

    @property
    def game_over(self):
        return self.duelo is not None and self.duelo.derrota

    def iniciar_duelo(self):
        if self.venceu_jogo:
            raise RuntimeError("O jogo já terminou: todos os chefes foram derrotados.")
        self.duelo = duelo(
            self.andar_atual,
            vidas_jogador=self.vidas_jogador,
            perguntas=self.carregador(self.andar_atual),
            rng=self.rng,
        )
        return self.duelo

    def avancar_andar(self):
        if self.duelo is None or not self.duelo.vitoria:
            raise RuntimeError("Só é possível subir depois de derrotar o chefe do andar.")

        self.chefes_derrotados.append(self.duelo.chefe["nome"])
        self.vidas_jogador = JOGADOR_VIDAS if RESTAURAR_VIDAS_POR_ANDAR else self.duelo.vidas_jogador
        self.duelo = None

        if self.andar_atual == TOTAL_ANDARES:
            self.venceu_jogo = True
            return False
        self.andar_atual += 1
        return True

    def reiniciar_andar(self):
        self.vidas_jogador = JOGADOR_VIDAS
        self.duelo = None


def verificar_relacao_perguntas_chefes(carregador=carregar_perguntas):
    problemas = []
    ids_vistos = {}
    dificuldade_anterior = 0
    vidas_anteriores = 0

    for andar in range(1, TOTAL_ANDARES + 1):
        chefe = obter_chefe(andar)
        perguntas = carregador(andar)

        if len(perguntas) != chefe["perguntas"]:
            problemas.append(
                f"Andar {andar}: o chefe espera {chefe['perguntas']} perguntas, "
                f"mas o arquivo tem {len(perguntas)}."
            )
        minimo = perguntas_necessarias(andar)
        if len(perguntas) < minimo:
            problemas.append(
                f"Andar {andar}: um duelo pode usar até {minimo} perguntas, "
                f"mas só há {len(perguntas)}; elas acabariam e teriam que se repetir."
            )
        if chefe["dificuldade"] <= dificuldade_anterior:
            problemas.append(f"Andar {andar}: a dificuldade não aumentou em relação ao andar anterior.")
        if chefe["vidas"] < vidas_anteriores:
            problemas.append(f"Andar {andar}: o chefe tem menos vidas que o do andar anterior.")
        dificuldade_anterior = chefe["dificuldade"]
        vidas_anteriores = chefe["vidas"]

        for p in perguntas:
            for erro in problemas_das_perguntas(p):
                problemas.append(f"Andar {andar}, pergunta {p.get('id')}: {erro}.")
            pid = p.get("id")
            if pid in ids_vistos:
                problemas.append(
                    f"Pergunta {pid} aparece nos andares {ids_vistos[pid]} e {andar}."
                )
            ids_vistos[pid] = andar

    return problemas

