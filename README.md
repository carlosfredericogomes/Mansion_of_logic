# Mansion of Logic

Jogo 2D em Python e pygame em que o jogador é um **Exterminador** preso em uma mansão de 4 andares. Para subir, ele derrota o chefe de cada andar em um **duelo de perguntas de lógica proposicional** (múltipla escolha).

Projeto da disciplina **Lógica para Computação**, CESAR School.

---

## Sumário

1. [Sobre o jogo](#sobre-o-jogo)
2. [Como o jogo funciona](#como-o-jogo-funciona)
3. [Requisitos](#requisitos)
4. [Instalação](#instalação)
5. [Como executar](#como-executar)
6. [Controles](#controles)
7. [Andares e chefes](#andares-e-chefes)
8. [Estrutura do projeto](#estrutura-do-projeto)
9. [Testes](#testes)
10. [Perguntas](#perguntas)
11. [Créditos e licenças](#créditos-e-licenças)
12. [Equipe](#equipe)

---

## Sobre o jogo

### Inspiração

*Mansion of Logic* é inspirado em uma **mansão do terror** que existia no parque **Mirabilândia**, em **Recife, Pernambuco**. A ideia foi levar essa atmosfera de casa assombrada, com andares, monstros e suspense, para dentro de um jogo.

### Objetivo didático

O jogo foi feito para ser **didático para estudantes** e para **praticar lógica** por meio das questões. Em vez de tratar a lógica como uma lista de exercícios, o jogador a usa para vencer: **acertar as questões é o que derrota os chefes** e permite subir pela mansão.

A dificuldade acompanha a progressão. Cada andar tem questões **fáceis, médias e difíceis** de acordo com a subida: o jogador começa com questões mais simples e chega ao último andar com as mais exigentes. Depois de um erro, o jogo mostra a **explicação da resposta certa**, para que o jogador aprenda com o erro.

### O que acontece no jogo

O jogador controla o **Exterminador**, que precisa escapar da mansão. Em cada andar há um **chefe** que bloqueia a subida. O Exterminador anda até o chefe e os dois se enfrentam em um duelo de perguntas de lógica. Cada resposta certa machuca o chefe, e cada resposta errada machuca o Exterminador. Quem ficar sem corações primeiro perde o duelo.

---

## Como o jogo funciona

1. No **menu**, o jogador aperta **Enter** (ou clica em **COMEÇAR**) e entra na mansão.
2. Na **exploração**, move o Exterminador com **W, A, S e D** (ou com as setas) até o encontro com o chefe do andar.
3. No **duelo**, aparece uma pergunta de lógica com 3 ou 4 alternativas:
   - **Acertou:** o Exterminador golpeia e o chefe perde 1 coração.
   - **Errou:** o chefe golpeia e o Exterminador perde 1 coração. A tela mostra a explicação da resposta certa.
4. Quando o chefe fica com 0 corações, o jogador **vence o andar** e ganha de 1 a 3 **estrelas**, conforme os corações que sobraram.
5. Se ainda dá para ganhar mais estrelas, o jogo oferece uma **nova chance** contra o mesmo chefe, sem reiniciar a partida. O andar fica com a **melhor** pontuação.
6. Se o Exterminador perde **todos os corações**, aparece a tela de **GAME OVER** e o jogo volta ao **menu**, para recomeçar do **andar 1**.
7. Ao derrotar o chefe do 4º andar, o jogador **vence o jogo** e vê a **pontuação final** (soma das estrelas dos 4 andares, de 0 a 12).

### Regras de vida

- O Exterminador tem **3 corações**, e eles **voltam a 3 ao passar para o próximo andar**.
- Cada coração é uma vida inteira (não há meio coração).
- Cada acerto ou erro vale exatamente 1 coração.
- Estrelas de cada andar: **3 corações = 3 estrelas, 2 corações = 2 estrelas, 1 coração = 1 estrela**. Uma nova chance no mesmo andar também começa com os 3 corações cheios.
- As perguntas de cada duelo são **sorteadas** (biblioteca `random`) e **não se repetem dentro do mesmo duelo**.
- Não há armas, equipamentos nem inimigos secundários.

---

## Requisitos

- **Python 3** (recomendado 3.10 ou superior)
- **pygame 2**
- **pytest** (só para rodar os testes)
- Tela de 1280×720 ou maior. O jogo desenha em 1280×720 e o pygame escala para a janela.

---

## Instalação

```bash
# 1. Clonar o repositório
git clone https://github.com/carlosfredericogomes/Mansion_of_logic.git
cd Mansion_of_logic

# 2. (Recomendado) criar um ambiente virtual
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux / macOS:
source .venv/bin/activate

# 3. Instalar as dependências
pip install -r requirements.txt
```

Se preferir instalar à mão: `pip install pygame pytest`.

---

## Como executar

Na pasta raiz do projeto:

```bash
python main.py
```

O jogo abre em **tela cheia** (desenha em 1280×720 a 60 FPS e o pygame escala para o monitor). Use **F11** para alternar entre tela cheia e janela. O jogo pode ser jogado **só com o teclado**; o mouse também funciona nos menus e nas alternativas.

---

## Controles

| Onde | Tecla ou ação | O que faz |
|---|---|---|
| Menu | `Enter` ou clique em **COMEÇAR** | Inicia o jogo |
| Exploração | `W` ou `↑` | Move o Exterminador para a frente |
| Exploração | `S` ou `↓` | Move o Exterminador para trás |
| Exploração | `A` ou `←` | Move o Exterminador para a esquerda |
| Exploração | `D` ou `→` | Move o Exterminador para a direita |
| Exploração | `Enter` ou `Espaço` | Pula a exploração e vai direto ao chefe |
| Duelo | Setas `↑` `↓` ou teclas `1` a `4` | Escolhe a alternativa |
| Duelo | `Enter` | Confirma a resposta e, depois do golpe, avança |
| Duelo | Mouse | Passar por cima destaca a alternativa e clicar confirma |
| Andar concluído | `↑` `↓` ou `1` e `2`, e `Enter` | Escolhe entre tentar de novo e continuar |
| Game over e vitória | `Enter` (ou clique) | Volta ao menu |
| Qualquer tela | `F11` | Alterna tela cheia |

---

## Andares e chefes

| Andar | Chefe | Corações do chefe | Perguntas no banco |
|---|---|---|---|
| 1 | Drácula | 3 | 6 |
| 2 | Frankenstein | 4 | 7 |
| 3 | Musashi (fantasma) | 5 | 8 |
| 4 | Lobisomem (chefe final) | 7 | 10 |

Total de **31 perguntas**. Cada banco cobre o pior caso de um duelo (vida do chefe + 3 − 1 perguntas) com 1 pergunta de sobra, e há um teste automático que garante isso.

---

## Estrutura do projeto

```
Mansion_of_logic/
├── assets/
│   ├── imagens/            # fundos, chefes, Exterminador (frente, costas e lado)
│   ├── fontes/             # DejaVu Sans (tem os símbolos lógicos)
│   └── sons/               # acerto, erro, vitória, game over (mp3) e passos
├── config/
│   └── config.py           # constantes: 1280x720, 60 FPS, caminhos, cores
├── perguntas/
│   ├── andar_1.json        # banco de perguntas de cada andar
│   ├── andar_2.json
│   ├── andar_3.json
│   └── andar_4.json
├── src/
│   ├── __init__.py
│   ├── chefes.py           # dados dos 4 chefes e vidas do jogador (sem pygame)
│   ├── progressao.py       # partida: andar atual, estrelas, nova chance e pontuação (sem pygame)
│   ├── questoes.py         # carrega e valida os JSON de perguntas (sem pygame)
│   ├── recursos.py         # carrega imagens, fontes e sons com cache
│   ├── regras.py           # estados, eventos, transições e motor de duelo (sem pygame)
│   ├── tela_conclusao.py   # tela de vitória (pontuação final e integrantes)
│   └── telas.py            # telas: exploração, duelo, andar concluído (estrelas) e game over
├── tests/
│   ├── test_regras.py
│   ├── test_progressao.py
│   ├── test_telas.py
│   └── test_jogo_completo.py   # o jogo inteiro rodando pelo main.py, só com teclado
├── .gitignore
├── CLAUDE.md
├── main.py                 # laço principal e troca de telas
├── README.md
└── requirements.txt        # dependências
```

**Regra de organização:** `regras.py`, `chefes.py` e `questoes.py` **não importam pygame**. Só `main.py`, `telas.py` e `recursos.py` usam. Assim, toda a lógica do jogo é testada com pytest sem abrir janela.

### Máquina de estados

| Estado | Significado |
|---|---|
| MENU | Tela inicial |
| S0 | Exploração do andar |
| S1 | Pergunta apresentada |
| S2 | Avaliação da resposta |
| S3 | Dano no chefe |
| S4 | Dano no jogador |
| S5 | Avanço de andar |
| S6 | Game over |
| VITÓRIA | Chefe do 4º andar derrotado |

Fluxo do duelo: **S0 → S1 → S2**. Acerto leva a S3, erro leva a S4. De S3 e S4, volta a S1 (próxima pergunta) até alguém chegar a 0 corações: chefe a 0 leva a S5, jogador a 0 leva a S6 (GAME OVER).

---

## Testes

Na pasta raiz:

```bash
python -m pytest
```

Os testes cobrem a máquina de estados, o carregamento e a validação das perguntas, o motor de duelo (acerto, erro, game over, pior caso nos 4 andares, sem repetição de perguntas), a progressão (estrelas, nova chance, pontuação e vitória), as telas (quebra de linha, golpes, mouse, exploração dos 4 andares, game over e vitória), os sons e uma partida completa do menu até a vitória.

---

## Perguntas

- As perguntas ficam em `perguntas/andar_N.json`, em **UTF-8**, e vêm da lista de exercícios de lógica da disciplina.
- A dificuldade sobe com os andares: **fáceis, médias e difíceis**, de acordo com a progressão.
- Cada pergunta tem enunciado, 3 ou 4 alternativas (o jogo as embaralha), a alternativa correta e uma explicação mostrada depois de um erro.
- Os enunciados usam símbolos como ∧, ∨, ¬, → e ↔, por isso o jogo usa a fonte **DejaVu Sans**, que tem todos eles.
- O validador (`questoes.py`) confere o formato e o tamanho dos bancos ao carregar.

---

## Créditos e licenças

| Recurso | Origem | Licença |
|---|---|---|
| pygame | https://www.pygame.org | LGPL |
| Fonte DejaVu Sans | https://dejavu-fonts.github.io | Licença livre da DejaVu (o texto está em `assets/fontes/`) |
| Efeitos sonoros (`assets/sons/`, exceto o game over) | Gerados por código pela própria equipe (ondas simples, sem material de terceiros) | Sem restrição |
| Lista de perguntas | Lista de exercícios da disciplina Lógica para Computação | Material da disciplina |

---

## Equipe

- Carlos Frederico
- Francisco Acioli
- Maria Carolina
- Maria Giulia

Disciplina: Lógica para Computação · CESAR School · 2026