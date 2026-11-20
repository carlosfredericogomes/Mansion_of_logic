from src.chefes import CHEFES, JOGADOR_VIDAS,TOTAL_ANDARES, obter_chefe,perguntas_necessarias
from src.questoes import carregar_perguntas
from src.regras import Duelo

PROXIMO_ANDAR = "PROXIMO_ANDAR"
VITORIA = "VITORIA"
GAME_OVER = "GAME_OVER"

class partida:
    def __init__(self):
        self.andar_atual = 1
        self.duelo = None
        self.chefes_derrotados = []
        self.venceu_jogo = False

    @property
    def chefe_atual(self):
        return obter_chefe(self.andar_atual)

    def iniciar_duelo(self, perguntas=None):
        if self.venceu_jogo:
            raise RuntimeError("o jogo terminou: lobisomem foi derrotado")
        if self.duelo is not None and not self.duelo.terminou:
            raise RuntimeError("já existe um duelo em andamento")
        self.duelo = Duelo(self.andar_atual, JOGADOR_VIDAS, perguntas)
        return self.duelo

    def concluir_duelo(self):
        if self.duelo is None or not self.duelo.terminou:
            raise RuntimeError("duelo ainda não terminou")
        duelo, self.duelo = self.duelo, None

        if duelo.game_over:
            self.andar_atual = 1
            self.chefes_derrotados = []
            return GAME_OVER

        self.chefes_derrotados.append(CHEFES[duelo.andar]["nome"])
        if self.andar_atual == TOTAL_ANDARES:
            self.venceu_jogo = True
            return VITORIA
        self.andar_atual += 1
        return PROXIMO_ANDAR

    def reiniciar(self):
        self.__init__()

def verificar_relacao_perguntas_chefes(carregador=carregar_perguntas):
    problemas = []
    ids_vistos = {}
    anterior = None

    for andar in range(1, TOTAL_ANDARES + 1):
        chefe = obter_chefe(andar)
        perguntas = carregador(andar)

        if len(perguntas) != chefe["perguntas"]:
            problemas.append(f"andar {andar}: o chefe espera {chefe['perguntas']} perguntas, mas o banco tem {len(perguntas)}")

        minimo = perguntas_necessarias(andar)
        if len(perguntas) < minimo:
           problemas.append (f"andar {andar}: o duelo pode usar ate {minimo} perguntas, mas só há {len(perguntas)}; o banco acabaria bo meio do duelo")

        if anterior is not None:
            if chefe["vidas"] <= anterior["vidas"]:
                problemas.append(f"andar{andar}: o chefe não tem mais coraçoes que o andar anterior")
            if chefe["perguntas"] <= anterior["perguntas"]:
                problemas.append(f"andar {andar}: o banco não é maior que o do andar anterior")
        anterior = chefe

        for p in perguntas:
            if len(set(p["opcoes"])) != len(p["opcoes"]):
                problemas.append(f"andar {andar}, perguntas {p["id"]}: tem alternativas repetidas")
            if p ["id"] in ids_vistos:
                problemas.append(f"pergunta {p['id']} aparece nos andares {ids_vistos[p['id']]} e {andar}")
            ids_vistos[p['id']] = andar

    return problemas
    