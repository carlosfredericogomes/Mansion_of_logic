JOGADOR_VIDAS = 3

CHEFES = {
    1: {"nome": "Lobisomem",    "vidas": 3, "perguntas": 6},
    2: {"nome": "Frankenstein", "vidas": 4, "perguntas": 7},
    3: {"nome": "Musashi",      "vidas": 5, "perguntas": 8},
    4: {"nome": "Drácula",      "vidas": 7, "perguntas": 10},
}

CUSTO_ACERTO = 1   
CUSTO_ERRO = 1  
RESTAURAR_VIDAS_POR_ANDAR = True

# informacoe sobre os chefes

CHEFES_INFOS = {
    1: {"nome": "lobisomem",
        "vidas": 3,
        "perguntas": 6,
        "dificuldade": 1,
        "rotulo_dificul": "Fácil",
        "tema": "Tradução simbólica e tabelas-verdade básicas",
        "imagem": "chefe_lobisomem.png",
        "fundo": "fundo_andar1.png",
        "fala_entrada": "Uivos ecoam pelo salão... Prove que sua lógica é afiada!",
        "fala_derrota": "O Lobisomem recua para as sombras. O caminho para cima está livre.",
     },

    2: { "nome": "Frankenstein",
        "vidas": 4,
        "perguntas": 7,
        "dificuldade": 2,
        "rotulo_dificul": "Médio",
        "tema": "Negação, bicondicional, absorção e modus ponens",
        "imagem": "chefe_frankenstein.png",
        "fundo": "fundo_andar2.png",
        "fala_entrada": "A criatura desperta entre faíscas. Cada erro a deixa mais forte!",
        "fala_derrota": "Os circuitos de Frankenstein se apagam. Siga para o próximo andar."
    },

    3: { "nome": "Musashi",
        "vidas": 5,
        "perguntas": 8,
        "dificuldade": 3,
        "rotulo_dificuldade": "Difícil",
        "tema": "Ou exclusivo, equivalências e classificação de fórmulas",
        "imagem": "chefe_musashi.png",
        "fundo": "fundo_andar3.png",
        "fala_entrada": "O guerreiro prepara sua espada. Apenas a precisão garante a vitória..",
        "fala_derrota": "Musashi faz uma reverência. Resta apenas o senhor da mansão.",
    },

    4: {"nome": "Drácula",
        "vidas": 7,
        "perguntas": 10,
        "dificuldade": 4,
        "rotulo_dificuldade": "Muito difícil",
        "tema": "Fórmulas compostas, equivalências e regras de inferência",
        "imagem": "chefe_dracula.png",
        "fundo": "fundo_andar4.png",
        "fala_entrada": "Bem-vindo ao topo da mansão. Daqui, poucos saem...",
        "fala_derrota": "Drácula vira pó ao amanhecer. A mansão está livre!",}
}

TOTAL_ANDARES = len(CHEFES)

def obter_chefe(andar):
    if andar not in CHEFES:
        raise ValueError(f"Andar inválido: {andar}. Use de 1 a {TOTAL_ANDARES}.")
    return dict(CHEFES[andar])

def perguntas_necessarias(andar, vidas_jogador=JOGADOR_VIDAS):
    chefe = obter_chefe(andar)
    acertos_max = -(-chefe["vidas"] // CUSTO_ACERTO)  
    erros_max = -(-vidas_jogador // CUSTO_ERRO)
    return acertos_max + erros_max - 1