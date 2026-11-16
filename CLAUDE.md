# CLAUDE.md — Mansion of Logic

Este arquivo é lido pelo Claude Code ao abrir a pasta do projeto. Ele reúne tudo o que a equipe conversou e decidiu sobre o jogo até **16/11/2026**. Quando houver conflito entre este arquivo e outro material, vale esta ordem:

1. **Seção 3 deste arquivo** (decisões de gameplay atuais da equipe) — manda em tudo que for regra de jogo.
2. O relatório técnico (seção 2) — referência acadêmica. Em 08 e 09/11/2026 a equipe decidiu **alterá-lo**: as partes 2.2, 2.3, 2.4, 2.5 e 2.6 saem do jogo, a 2.7 foi simplificada e os inimigos secundários saíram da 2.1. O resto do relatório continua como está.
3. O cronograma publicado — serve só para guiar as tarefas de código (seção 9). Onde ele diverge da seção 3, a seção 3 vence (ver seção 4).

---

## 0. Como o Claude deve trabalhar neste projeto (regras permanentes do usuário)

O usuário pediu que estas três regras sejam seguidas **sempre**:

1. **Não fazer nada além do que foi pedido.** Só ir além quando for realmente necessário, e nesse caso **perguntar antes**, explicando o contexto de como aquilo seria útil.
2. **Não tirar do contexto** do que já foi conversado e decidido sobre o jogo (este arquivo é esse contexto).
3. **Explicar tudo** o que foi sugerido, alterado ou feito, sem omitir nada.

Outras orientações que o usuário deu ao longo do projeto:

- O cronograma só guia, em etapas, as tarefas de código e não altera o relatório por conta própria. A equipe decidiu em 08/11/2026 alterar o relatório nos itens da seção 2 (2.2, 2.3, 2.4, 2.5, 2.6 removidos, 2.7 simplificada e inimigos secundários removidos da 2.1). Fora esses itens, **perguntar antes de mexer** no que o relatório diz.
- **Não inventar nem alterar perguntas** da Lista Extra. Só selecionar e distribuir entre os andares. Só usam as partes 1 a 5 da lista (a parte 6 foi excluída).
- Não adicionar informações irrelevantes e não fugir muito do que está proposto no relatório (com as alterações da seção 2).
- Em dúvida de escopo ou de regra de jogo, **perguntar** em vez de decidir sozinho.
- Responder em português do Brasil. O usuário e a equipe são estudantes da CESAR School (disciplina Lógica para Computação, equipe de 5 pessoas).

---

## 1. Visão geral

- **Jogo:** Mansion of Logic, RPG tático em turnos, 2D, em **Python + pygame 2**.
- **Tela:** resolução base **1280×720**, **60 FPS** (definidos em `config`), janela aberta com `pygame.SCALED | pygame.RESIZABLE`, tecla **F11** alterna tela cheia. O jogo sempre desenha na resolução base e o pygame escala para telas de 1366×768, 1920×1080 etc.
- **Premissa:** o jogador é um **Exterminador** que escapa de uma mansão de **4 andares**. Para subir, derrota o chefe de cada andar. O combate de cada chefe é um **duelo de perguntas de lógica proposicional** (múltipla escolha).
- **Prazo de entrega:** **22/11/2026**.
- **Origem acadêmica:** o relatório técnico usa Lógica Proposicional para formalizar o jogo. A parte de variáveis, condições de dano (D1 a D4), DNF/CNF e SAT **foi removida do jogo** (seção 2). O jogo não tem sistema de dano por fórmulas: o dano vem só de acerto ou erro nas perguntas.

---

## 2. Relatório técnico (referência acadêmica, alterado pela equipe em 08/11/2026)

Título: *Modelagem Lógico-Proposicional e Arquitetura de Regras para o Jogo Mansion of Logic* (3 páginas).

**Situação em 09/11/2026:** o jogo é simples. **Acertou a pergunta, o chefe perde 1 coração. Errou, o Exterminador perde 1 coração. Nada além disso**, sem armas ou equipamentos diferentes. Ficam **removidos**: 2.2 (variáveis), 2.3 (condições de dano), 2.4 (tabela-verdade de D1), 2.5 (formas normais) e 2.6 (SAT e softlocks). A **2.7 (máquina de estados) foi simplificada** (abaixo). Os **inimigos secundários saíram do planejamento**. A 2.1 continua, com a coluna de temática mantida (ver 3.9).

### 2.1 Andares e chefes

| Andar | Chefe | Temática de combate |
|---|---|---|
| 1º | Lobisomem | Fraqueza à Prata e Contra-Ataque |
| 2º | Frankenstein | Resistência e Combinação Fogo/Item |
| 3º | Miyamoto Musashi (Fantasma) | Imaterialidade e Esquiva Sagrada |
| 4º | Drácula (Boss Final, o mais perigoso, é um vampiro) | Sincronia Estaca + Fogo em Vulnerabilidade |

Os **inimigos secundários** (Lobos Menores, Zumbis Normais, Aparições Normais e Vampiros Comuns) **saíram do planejamento do jogo**. A coluna de temática foi **mantida** de propósito, por causa da ideia de troca automática de arma por andar (seção 3.9). Hoje a temática não muda nenhuma regra.

### 2.2 Variáveis (V = {0, 1}) — REMOVIDO do jogo

Eram as variáveis `a, d, i, p, f, s, m, c, v`. **Não implementar.** Não existe mais `regras.py` com essas variáveis.

### 2.3 Condições de dano — REMOVIDO do jogo

Eram as fórmulas D1 a D4 de dano por andar. **Não implementar.** O dano agora é só o da seção 3.1 e 3.7 (acerto tira 1 coração do chefe, erro tira 1 do Exterminador).

### 2.4 Tabela-verdade de D1 — REMOVIDO do jogo

Era a tabela-verdade da condição D1. **Não implementar.**

### 2.5 Formas normais (DNF/CNF) — REMOVIDO do jogo

Era o exemplo de DNF e CNF da fórmula D2. **Não implementar.**

### 2.6 SAT e ausência de softlocks — REMOVIDO do jogo

Era a prova de satisfatibilidade de D1 a D4. **Não implementar.** O risco de travar a partida agora vem só de banco de perguntas pequeno demais ou de bug, e é coberto pelo teste do tamanho do banco (seção 3.2).

### 2.7 Máquina de estados (FSM) — SIMPLIFICADA pela equipe (09/11/2026)

Sem fórmulas, sem armas e sem inimigos secundários, a máquina de estados fica assim:

| Estado atual | Evento / condição | Próximo estado | Ação |
|---|---|---|---|
| S0 Exploração | Encontro com o chefe | S1 Pergunta apresentada | Carrega o andar e sorteia a pergunta |
| S1 Pergunta apresentada | Jogador confirma uma alternativa | S2 Avaliação da resposta | Confere se acertou ou errou |
| S2 Avaliação | Acertou | S3 Dano no Chefe | Chefe perde 1 coração |
| S2 Avaliação | Errou | S4 Dano no Jogador | Exterminador perde 1 coração |
| S3 Dano no Chefe | Chefe com 0 corações | S5 Avanço de Andar | Desbloqueia o próximo andar |
| S3 Dano no Chefe | Chefe ainda com corações | S1 | Sorteia a próxima pergunta |
| S4 Dano no Jogador | Jogador com 0 corações | S6 Game Over | Volta ao andar 1 |
| S4 Dano no Jogador | Jogador ainda com corações | S1 | Sorteia a próxima pergunta |

Além de S0 a S6, o jogo tem **MENU** (início) e **VITÓRIA** (depois de vencer o Drácula no 4º andar). As linhas que voltam a S1 não estão escritas assim no relatório; foram deduzidas do fluxo do duelo (a equipe só disse que acerto tira coração do chefe e erro tira do jogador).

---

## 3. Decisões de gameplay atuais (equipe, 05/11/2026) — AUTORIDADE

### 3.1 Vidas e corações

- O **Exterminador tem 3 vidas (3 corações)**, representadas como corações na tela, **durante todo o jogo**.
- Cada chefe também tem vidas representadas como corações:

| Andar | Chefe | Vidas (corações) do chefe | Questões no banco do andar |
|---|---|---|---|
| 1 | Lobisomem | 3 | 6 |
| 2 | Frankenstein | 4 | 7 |
| 3 | Musashi (Fantasma) | 5 | 8 |
| 4 | Drácula | 7 | 10 |

- **Custo de cada acerto ou erro = 1 vida (1 coração).**
  - **Acerto:** o chefe perde 1 coração.
  - **Erro:** o Exterminador perde 1 coração.
- Chefe com 0 corações: o jogador vence o andar. Exterminador com 0 corações: **game over** (decisão anterior mantida: volta ao andar 1).
- Não existe mais meio coração. Cada coração é 1 vida inteira.

### 3.2 Perguntas e sorteio

- Cada andar tem o seu **banco de perguntas**, guardado em arquivo (seção 5). As perguntas do andar são as da tabela acima (6, 7, 8 e 10).
- O jogo usa a **biblioteca `random`** para sortear as perguntas que aparecem na tela.
- Uma mesma pergunta **não deve repetir dentro do mesmo duelo**.
- Conferência do tamanho dos bancos (pior caso de um duelo = vida do chefe + 3 − 1 perguntas, que é quando o jogador erra 2 vezes e só então derrota o chefe):

| Andar | Pior caso (vida do chefe + 3 − 1) | Banco decidido | Sobra |
|---|---|---|---|
| 1 | 3 + 3 − 1 = 5 | 6 | 1 |
| 2 | 4 + 3 − 1 = 6 | 7 | 1 |
| 3 | 5 + 3 − 1 = 7 | 8 | 1 |
| 4 | 7 + 3 − 1 = 9 | 10 | 1 |

  Ou seja, o banco de cada andar cobre o pior caso com 1 pergunta de sobra. Um teste automático deve garantir isso.
- Total: 6 + 7 + 8 + 10 = **31 perguntas** (o plano antigo falava em 33).

### 3.3 Dados sugeridos para `chefes.py` (sugestão, sem pygame)

```python
JOGADOR_VIDAS = 3

CHEFES = {
    1: {"nome": "Lobisomem",    "vidas": 3, "perguntas": 6},
    2: {"nome": "Frankenstein", "vidas": 4, "perguntas": 7},
    3: {"nome": "Musashi",      "vidas": 5, "perguntas": 8},
    4: {"nome": "Drácula",      "vidas": 7, "perguntas": 10},
}
CUSTO_ACERTO = 1   # corações que o chefe perde
CUSTO_ERRO = 1     # corações que o jogador perde
```

### 3.4 Itens ainda em aberto (perguntar à equipe antes de codificar)

1. **Vidas do jogador entre andares:** "3 vidas durante todo o jogo" significa que os 3 corações **não** voltam ao vencer um chefe, ou que voltam a 3 em cada andar? O plano antigo restaurava toda a vida ao vencer um chefe. Confirmar.
2. ~~Andar 2 tem 8 perguntas, decisão é 7.~~ **RESOLVIDO (até 15/11/2026):** a pergunta **89** saiu e o andar 2 ficou com 7 (seção 5.2).
3. **Sequência de acertos (combo) e dica:** continuam existindo? Eram opcionais. Com o custo de 1 coração, o combo (3 acertos seguidos) tiraria 1 coração extra do chefe. A dica elimina 1 alternativa errada (1 uso por chefe). Confirmar se entram.
4. **Nível (fácil, médio, difícil) por pergunta nos andares 2 e 3** ainda não está registrado oficialmente. O andar 1 é de nível fácil e o andar 4 foi pedido com questões médias.
5. **Preferência de não repetir perguntas após um game over** (priorizar as que o jogador ainda não viu) foi uma decisão antiga. Com bancos tão pequenos ela ainda faz sentido, mas confirmar. (O `Duelo` implementado só sorteia dentro do duelo, sem memória entre partidas.)
6. **Enunciados alterados no andar 4 (visto no vídeo de 10/11/2026):** a pergunta 13 ganhou "(p = Maria estuda, …)", e a 41 e a 47 foram reescritas como "montamos a tabela… qual coluna de resultado". A regra da seção 5.1 só permite acrescentar a frase da coluna de resultado nas tabelas-verdade. A equipe precisa aceitar ou voltar ao original. O desfecho não foi informado.
7. **Janela abre em tela cheia?** O resumo do Claude Code de 15/11 diz que o jogo abre em tela cheia (F11 alterna). A seção 1 só prevê `SCALED | RESIZABLE` com F11. Confirmar se foi escolha da equipe.
8. **Revisão das alternativas erradas e das explicações** das perguntas (pendente da equipe, checklist 9.4).

### 3.5 Substituído por 3.1 e 3.2 (não usar mais)

- Vida do jogador de 6 pontos (6 = 3 corações, meio coração = 1 ponto).
- Vida dos vilões de 2, 3, 4 e 5 pontos e custo do erro de 2, 2, 2 e 3 pontos.
- Mistura de níveis por andar (100% fácil; 60/40 fácil/médio; 70/30 médio/difícil; 25/75 médio/difícil) e as chances de vitória calculadas com ela.
- Pior caso de 4, 5, 6 e 6 perguntas por duelo e banco de 33 perguntas.
- Andar 1 com 7 fáceis, andar 2 com 5 fáceis e 3 médias, andar 3 com 7 médias e 3 difíceis, andar 4 com 2 médias e 6 difíceis.
- Menus de ação e de equipamento (c11 e c12), variáveis, D1–D4, DNF/CNF e SAT (ver 3.6).

### 3.6 Sistema de dano por fórmulas (D1 a D4): REMOVIDO (08/11/2026)

- A equipe decidiu que o jogo **não usa** variáveis de ação e equipamento, nem condições de dano D1 a D4, nem DNF/CNF, nem prova SAT (relatório 2.2, 2.3, 2.5 e 2.6).
- **Não criar** funções D1–D4, variáveis `a, d, i, p, f, s, m, c, v` nem testes para elas. Tarefas do cronograma que eram só para isso foram **retiradas**: c5, c6, c11 e c12 (e o c9 passou a testar só a máquina de estados).
- O dano do jogo é só o de 3.1 e 3.7: acerto tira 1 coração do chefe e erro tira 1 coração do Exterminador. **Sem armas ou equipamentos diferentes.** A única ideia em análise é a troca automática de arma a cada andar (seção 3.9), que não muda o dano.
- As discussões anteriores sobre a fórmula D2 e o exemplo de SAT deixaram de valer.

### 3.7 Dano no Exterminador quando ele erra a pergunta

**Regra:** cada resposta errada tira **exatamente 1 coração** do Exterminador (`CUSTO_ERRO = 1`). O erro **não mexe na vida do chefe**, e o acerto **não mexe na vida do jogador**. A vida do jogador nunca fica abaixo de 0.

**Fluxo de um erro (usa a máquina de estados da seção 2.7):**

1. O jogador confirma uma alternativa (S1 → S2 Avaliação). Aqui a avaliação é só "acertou ou errou"; não há fórmula Dn.
2. **Errou → S4 Dano no Jogador:** `vidas_jogador = max(0, vidas_jogador - CUSTO_ERRO)`.
3. Feedback na tela: a alternativa escolhida em **vermelho**, a certa em **verde**, a **explicação** da resposta certa, e o **coração perdido some** do indicador de vida.
4. Se `vidas_jogador > 0`: sorteia a próxima pergunta (sem repetir no duelo) e volta a S1.
5. Se `vidas_jogador == 0`: **S6 Game Over** e o jogo volta ao andar 1 (decisão anterior). *Proposta, a confirmar com a equipe:* a explicação do último erro aparece antes da tela de game over.
6. Para comparar, o **acerto** vai para S3 Dano no Chefe (chefe perde 1 coração). Chefe com 0 corações vai para S5 Avanço de Andar.

**Em que pasta e arquivo isso é feito:** tudo na pasta **`src/`** (a pasta de testes é `tests/`).

| O que | Onde |
|---|---|
| Constantes `JOGADOR_VIDAS = 3` e `CUSTO_ERRO = 1`, junto com os dados dos chefes | `src/chefes.py` |
| **A lógica do dano:** aplicar o erro, reduzir a vida, verificar fim do duelo e a transição S2 → S4 → S6 (sem `pygame`) | `src/regras.py` (motor de duelo, tarefa c23, e `proximo_estado`, tarefa c8) |
| Testes do dano por erro | `tests/test_regras.py` (tarefa c24) |
| Corações do jogador na tela, vermelho e verde, explicação | `src/telas.py` (arquivo criado nas tarefas c10 e c26; ele só desenha, não decide dano) |
| Ligar tudo no laço do jogo | `main.py` (tarefa c13), que apenas chama as funções acima |

Regra de arquitetura: **quem decide o dano é `regras.py`; quem mostra é `telas.py`.** Assim o teste do dano roda com pytest sem abrir janela.

**Exemplo de forma (sugestão, não é código final):**

```python
def responder(duelo, indice_escolhido):
    acertou = indice_escolhido == duelo.pergunta_atual.correta   # posição após embaralhar as opções
    if acertou:
        duelo.vidas_chefe = max(0, duelo.vidas_chefe - CUSTO_ACERTO)
    else:
        duelo.vidas_jogador = max(0, duelo.vidas_jogador - CUSTO_ERRO)
    return acertou
```

**Testes que cobrem o erro** (`tests/test_regras.py`):

- Um erro tira exatamente 1 coração do jogador e nenhum do chefe.
- Um acerto tira 1 coração do chefe e nenhum do jogador.
- Três erros seguidos levam a 0 corações e ao game over (S6).
- A vida do jogador nunca fica negativa, mesmo com mais erros depois de zerar.
- Dois erros e depois acertos até zerar o chefe: o jogador vence com 1 coração (pior caso de cada andar).

**Ainda em aberto, e afeta o que acontece depois do erro:** se os 3 corações voltam ao vencer um chefe ou não (seção 3.4, item 1).

### 3.8 Respostas da equipe sobre o relatório alterado (09/11/2026)

1. **Máquina de estados (2.7):** o jogo é simples. Acertou, o chefe perde 1 coração; errou, o Exterminador perde 1 coração. Nada além disso, sem armas diferentes. Registrada na seção 2.7.
2. **Tabela-verdade de D1 (2.4):** removida.
3. **Quadro dos andares (2.1), coluna de temática:** mantida, por causa da ideia da seção 3.9.
4. **Inimigos secundários:** removidos do planejamento. A tarefa c16 foi retirada.

### 3.9 Ideia em análise: troca automática de arma a cada andar (NÃO decidida)

- A equipe quer analisar fazer o Exterminador **trocar de arma automaticamente a cada andar**, porque acha que fica mais interessante. É "algo a ser analisado ainda": **não é regra, não é tarefa e não deve ser implementada** sem a equipe confirmar.
- É por isso que a coluna "Temática de combate" da seção 2.1 foi mantida (Prata, Fogo/Item, Relíquia Sagrada, Estaca + Fogo). O uso dela como a arma de cada andar é uma leitura minha, a confirmar.
- Pelo que a equipe disse ("sem armas diferentes"), a troca **não muda o dano**: acerto e erro continuam tirando 1 coração. O que a troca mudaria de fato (por exemplo só o desenho do Exterminador em cada andar) ainda precisa ser definido.
- Se for aprovada, ela provavelmente pede **artes novas** (uma versão do Exterminador por andar) e uma tarefa no cronograma. Hoje existe só uma arte do Exterminador de frente (`jogador_exterminador.png`) e uma de costas (para a exploração).

### 3.10 Movimentação na exploração com W, A, S, D ou setas (16/11/2026)

- **Pedido da equipe (16/11/2026):** nos momentos de exploração do jogador (andar até a escada para subir de andar, achar o chefe etc.), o jogador usa **`W`, `A`, `S`, `D` ou as setas do teclado** para movimentar o Exterminador. As duas formas valem ao mesmo tempo.
- **Tarefa nova no cronograma: c41** (Etapa 4, 2 h, logo depois da c36). O cronograma foi alterado **só** para acrescentar essa tarefa.
- **Como deve ser (movimento simples):** 4 direções, velocidade em função do `dt` (igual em qualquer computador), o personagem não sai da área do andar, a diagonal não deixa mais rápido. A leitura das teclas fica em `main.py` e a tela de exploração em `src/telas.py` (`TelaExploracao`). As setas continuam servindo para escolher respostas na tela de pergunta (c26); a leitura do movimento só vale no estado S0.
- **Efeito sobre a c36:** hoje a `TelaExploracao` é uma **caminhada automática** (3 cenas, Enter pula). O texto da c36 no cronograma ("uma tecla avança até o encontro com o chefe") **ainda não foi alterado** e conflita com a c41. Perguntar à equipe como adaptar a c36 antes de mexer.
- **Escopo (seção 9.2):** movimento simples entra; "movimentação elaborada", mapa livre e colisão com paredes continuam **fora** a menos que a equipe peça.

---

## 4. Divergências entre o cronograma publicado e a seção 3 (a atualizar)

O cronograma publicado (artifact em `https://claude.ai/artifact/RrZGr4Bzi4nhyKd9n8qs88`, versão 16, com a c41 acrescentada em 16/11) ainda traz as regras antigas nestas tarefas. **Exceção:** o trecho do dano no Exterminador ao errar (seção 3.7) já foi atualizado em c23, c24, c26 e c10. **Antes de implementar, seguir a seção 3**; o cronograma será atualizado depois que a equipe confirmar:

| Tarefa | O que o cronograma diz | O que vale agora |
|---|---|---|
| c37 | vida do jogador de 6 pontos, vilões com 2, 3, 4, 5 pontos, erro custando 2, 2, 2, 3, vida recuperada ao vencer, banco de 33 | 3 corações, chefes com 3, 4, 5, 7, custo 1, banco de 31 |
| c22 | formato com vida em pontos e mistura de níveis por andar | vidas em corações e bancos de 6, 7, 8 e 10 |
| c23 | (dano por erro já atualizado) o sorteio ainda fala em mistura de níveis e troca de pergunta após erro | custo 1 para todos; sorteio com `random`, sem repetir no duelo |
| c24 | (testes do dano por erro já atualizados) o tamanho do banco ainda fala em mínimo por nível | testar bancos de 6, 7, 8, 10 contra o pior caso |
| c25 | andar 1 com 7 fáceis, andar 2 com 5 fáceis e 3 médias (15) | andar 1 com 6, andar 2 com 7 (já definido: a 89 saiu) |
| c36 | "uma tecla avança até o encontro com o chefe" | a exploração passa a ter movimento com W, A, S, D ou setas (c41, seção 3.10); a c36 precisa ser adaptada |
| c27 | andar 3 com 10 (7 médias e 3 difíceis), andar 4 com 8 (2 médias e 6 difíceis) | andar 3 com 8, andar 4 com 10 médias |
| c10 | (já atualizado) corações inteiros para jogador e chefe | corações inteiros para jogador e chefe |
| c15 | restaura toda a vida do jogador ao vencer um chefe | depende da decisão 3.4 item 1 |
| c29, c30 | sequência de acertos e dica | opcionais, depende da decisão 3.4 item 3 |
| c28 | trocar o plano de cada vilão por pontos e níveis | ajustar corações e perguntas |

Em 08 e 09/11/2026 as tarefas **c5, c6, c11, c12 e c16 foram retiradas** do cronograma (variáveis, D1–D4, menus de ação e equipamento, e inimigos secundários). Também foram ajustados o c7 (estados), o c9 (só máquina de estados) e o c19 (sem "combinações que nunca dão dano").

---

## 5. Banco de perguntas

### 5.1 Fonte e regras

- Fonte única: **Lista Extra** de Lógica para Computação (professor Guilherme Fernando Cavalcanti Pereira), partes **1 a 5**: Simbolização de Proposições, Tabelas-Verdade, Equivalências Lógicas, Tautologias/Contradições/Contingências e Método Dedutivo. A parte 6 (tradução de página de livro) está excluída.
- **Não inventar nem alterar enunciados.** Só selecionar. A única mudança permitida até agora foi acrescentar, nas questões de tabela-verdade, a frase "Qual é a coluna do resultado, nas linhas VV, VF, FV, FF?", para caber em múltipla escolha.
- As **alternativas erradas e as explicações** não existem na lista. Os rascunhos feitos para o andar 1 precisam de revisão da equipe.

### 5.2 Questões por andar (número é o da Lista Extra)

**1º andar — 6 questões**
- (1) Traduza para a linguagem simbólica: “Se chover, então levo guarda-chuva.”
- (2) Traduza: “Maria é engenheira e João é advogado.”
- (21) Monte a tabela-verdade de p ∧ q.
- (24) Monte a tabela-verdade de p → q.
- (44) Simplifique ¬(¬p).
- (61) Classifique p ∨ ¬p como tautologia, contradição ou contingência.

**2º andar — 7 questões (a 89 saiu; o JSON já está com 7)**
- (81) A partir de p → q e p, deduza q.
- (4) Traduza: “Não é verdade que Ana viajou.”
- (25) Monte a tabela-verdade de p ↔ q.
- (51) Simplifique p ∨ (p ∧ q).
- (62) Classifique p ∧ ¬p.
- (3) Traduza: “Se Pedro estuda ou trabalha, então ele está cansado.”
- (26) Monte a tabela-verdade de (p ∨ q) ∧ ¬r.
- ~~(89) De p ∨ q e ¬p, deduza q.~~ (removida)

**3º andar — 8 questões**
- (5) Traduza: “Ou Paulo é médico ou Paulo é dentista, mas não ambos.”
- (28) Monte a tabela-verdade de (p ∨ q) → (p ∧ q).
- (19) Traduza: “Se o motor funciona, o carro anda; caso contrário, ele para.”
- (47) Prove que p ↔ q é equivalente a (p → q) ∧ (q → p).
- (63) Verifique se (p → q) ∨ (q → p) é tautologia.
- (65) Determine se (p ∨ q) → (p ∧ q) é contingência.
- (83) De p → q e q → r, deduza p → r.
- (17) Traduza: “Nenhum aluno faltou à aula.” (atenção: usa quantificador, e o jogo só usa lógica proposicional; a equipe deve decidir se mantém)

**4º andar — 10 questões (todas médias, nenhuma repetida de outro andar)**
- (7) Traduza: “Se hoje é sábado e está sol, irei à praia.”
- (13) Traduza: “Se Maria não estuda, então ela não passa.”
- (27) Monte a tabela-verdade de (p → q) ∨ (¬p).
- (41) Mostre que p → q é logicamente equivalente a ¬p ∨ q.
- (82) De p → q e ¬q, deduza ¬p. (no PDF o enunciado termina com um "(" solto, que foi omitido por parecer erro de digitação)
- (98) Deduzir ¬p ∨ q a partir de p → q.
- (42) Demonstre a equivalência de ¬(p ∧ q) e ¬p ∨ ¬q (Lei de De Morgan).
- (37) Monte a tabela-verdade de (p ∨ q) ↔ (¬p → q).
- (64) Determine se (p ∧ q) → (p ∨ q) é tautologia.
- (68) Classifique (p → q) ∧ (p → ¬q).

Critério usado para "média": até 2 variáveis, poucos conectivos e poucos passos. As difíceis têm 3 variáveis ou várias etapas. Cada tema aparece 2 vezes no andar 4.

### 5.3 Formato do arquivo `perguntas/andar_N.json` (UTF-8)

```json
{
  "andar": 1,
  "perguntas": [
    {
      "id": 1,
      "tema": "Simbolização de Proposições",
      "nivel": 1,
      "enunciado": "Traduza para a linguagem simbólica: “Se chover, então levo guarda-chuva.”",
      "opcoes": ["p → q", "p ∧ q", "p ∨ q", "q → p"],
      "correta": 0,
      "explicacao": "“Se ..., então ...” é uma condicional (→). Com p = chover e q = levo guarda-chuva, fica p → q."
    }
  ]
}
```

- `id`: número da questão na Lista Extra. `nivel`: 1 fácil, 2 média, 3 difícil.
- `opcoes`: de 2 a 4 alternativas (a questão 61 tem só 3). `correta`: posição (começando em 0) da certa em `opcoes`. O jogo **embaralha as opções** ao mostrar, para a certa não ficar sempre na tecla 1.
- `explicacao`: aparece depois de um erro.
- Rascunho do andar 1 já feito (respostas conferidas): 1 → p → q; 2 → p ∧ q; 21 → V, F, F, F; 24 → V, F, V, V; 44 → p; 61 → Tautologia.
- Em tabelas-verdade, a coluna do resultado vem nas linhas VV, VF, FV, FF.

### 5.4 Regras do carregador (`src/questoes.py`)

- Lê os JSON de `perguntas/`, valida o formato (campos obrigatórios, `correta` dentro de `opcoes`, 2 a 4 opções) e devolve as perguntas do andar.
- Não conhece `pygame`.
- Se faltar pergunta no banco, mostrar um aviso claro em vez de travar o jogo.
- **Situação (resumo do Claude Code, 15/11/2026):** implementado. `validar_pergunta` e `carregar_perguntas(andar)`. Formato inválido levanta `ValueError` (arquivo, pergunta e campo); arquivo ausente ou banco menor que o esperado dá só um aviso. O carregador **não embaralha**: o sorteio e o embaralhamento das opções ficam na classe `Duelo` (`regras.py`), que também usa `BancoInsuficiente` se as perguntas acabarem.

---

## 6. Estrutura do repositório

### 6.1 Estrutura combinada

```
Mansion_of_logic/
├── main.py
├── README.md
├── requirements.txt
├── .gitignore
├── assets/
│   ├── imagens/
│   ├── sons/
│   └── fontes/
├── perguntas/
│   ├── andar_1.json
│   ├── andar_2.json
│   ├── andar_3.json
│   └── andar_4.json
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── regras.py
│   ├── chefes.py
│   ├── questoes.py
│   ├── telas.py
│   └── recursos.py
└── tests/
    └── test_regras.py
```

`telas.py` e `recursos.py` foram sugestão e só são criados quando as tarefas correspondentes chegarem.

### 6.2 Situação real vista no VS Code (04/11/2026)

- Existem: `__pycache__/` na raiz, `assets/` (com subpasta `assets MOL` e `.gitkeep`), `config/config.py`, `perguntas/andar_1.json` a `andar_4.json`, `src/__init__.py`, `src/chefes.py`, `src/regras.py`, `tests/test_regras.py`, `main.py`, `README.md`, `requirements.txt`.
- Pontos a ajustar (recomendados, ainda não confirmados pela equipe):
  1. **Sem `.gitignore`:** criar com `__pycache__/` e `*.pyc` e tirar do Git o que já foi enviado (`git rm -r --cached`).
  2. **`assets MOL` tem espaço no nome:** reorganizar em `assets/imagens`, `assets/sons`, `assets/fontes`.
  3. **`config/` fica na raiz**, mas o cronograma prevê `src/config.py`. Mover para `src/config.py` ou atualizar o texto da tarefa c31.
  4. Havia um arquivo `.pyc` aberto no editor (`config/__pycache__/...`); não editar arquivos gerados.
  5. `src/questoes.py`, `telas.py` e `recursos.py` ainda não existem (normal).
- A pasta `perguntas/` com JSON na raiz é uma boa decisão e substitui a ideia antiga de guardar as perguntas dentro de um `questoes.py`. (Hoje `src/questoes.py` existe, mas só como carregador e validador dos JSON; ver 6.3.)

### 6.3 Situação do código em 15/11/2026 (vídeo de 10/11 e resumo do Claude Code de 15/11)

Fonte: o vídeo de 10/11 (VS Code) e o resumo que o Claude Code deu à equipe em 15/11. **Eu não vi o código nem rodei o pytest**; o que está abaixo é o que foi relatado.

- **Existem:** `main.py`, `config/config.py` (continua em `config/` na raiz, **não** em `src/config.py`), `src/chefes.py`, `src/questoes.py`, `src/regras.py`, `src/recursos.py`, `src/telas.py`, `tests/test_regras.py`, `tests/test_telas.py`, `.gitignore` (ignora `__pycache__/` e `*.pyc`), `assets/fontes/` (DejaVu Sans normal e negrito e o texto da licença) e `perguntas/andar_1.json` a `andar_4.json`.
- **`src/chefes.py`:** `JOGADOR_VIDAS = 3`, os 4 chefes (corações 3, 4, 5 e 7; perguntas 6, 7, 8 e 10), `CUSTO_ACERTO = CUSTO_ERRO = 1`.
- **`src/regras.py`:** enums `Estado` (S0 a S6) e `Evento`, `TRANSICOES` (8 transições), `proximo_estado` (levanta `ValueError` em transição inválida), `embaralhar_opcoes` e a classe `Duelo(andar, vidas_jogador, perguntas)`. As vidas do jogador entram como parâmetro porque a decisão 3.4 item 1 está em aberto. `responder(i)` passa por S2, aplica o dano com `max(0, …)` e avança para S5, S6 ou volta a S1. `proxima_pergunta()` é uma chamada separada para a tela mostrar o feedback antes de trocar. Propriedades `terminou`, `venceu` e `game_over`.
- **`src/telas.py`:** `quebrar_texto` (c34), `desenhar_coracao`, `TelaExploracao` (S0, **caminhada automática** de 3 cenas, Enter pula, a c36 adiantada) e `TelaDuelo` (fases PERGUNTA e FEEDBACK, setas ou 1 a 4 e Enter, piscada verde ou vermelha, explicação no erro).
- **`main.py`:** três estados, MENU → EXPLORACAO → JOGO. O clique em COMEÇAR inicia a exploração, que ao terminar cria `TelaDuelo(Duelo(1))`. Usa `dt` limitado a 0,1 s. Abre em tela cheia, e F11 alterna. **Ao fim do duelo volta ao menu (provisório).**
- **`perguntas/andar_2.json`:** a pergunta 89 saiu (7 perguntas).
- **Testes relatados:** máquina de estados, validador e carregador, duelo (erro, acerto, game over, pior caso nos 4 andares, sem repetição, correta depois de embaralhar, banco esgotado), tamanho dos bancos, quebra de linha e símbolos da fonte. O teste de "vida do jogador nunca fica negativa" **não foi citado** no resumo, e o resumo não informa quantos testes passaram.
- **Pendências de código:** teste real do duelo no monitor com mouse e teclado (c39); **commit, revisão e merge** (`config.py`, `main.py`, `questoes.py`, `regras.py`, `test_regras.py`, `recursos.py`, `telas.py`, `test_telas.py` e `assets/fontes/` estavam sem commit); conferir se as artes de fato estão em `assets/imagens` (se faltar arquivo, `recursos.py` mostra um retângulo provisório e avisa no terminal); créditos da DejaVu Sans no README (c21).
- **Ainda não existem:** progressão entre andares e saídas de S5 e S6 (c15), telas de vitória, game over e menu como estados (c18), MENU e VITÓRIA no enum, andares 2 a 4 no `main.py`, chefes 3 e 4 em uso, sons e a movimentação com W, A, S, D e setas (c41).

---

## 7. Convenções técnicas

- **Python** com **pygame 2**; testes com **pytest** rodados da raiz: `python -m pytest`. Dependências: `pip install pygame pytest` (ambiente virtual por pessoa).
- **Separar regras do pygame:** `regras.py`, `chefes.py` e `questoes.py` **não importam `pygame`**. Só a interface (`main.py`, `telas.py`, `recursos.py`) usa pygame. Isso permite testar tudo com pytest sem abrir janela.
- **Constantes** (largura, altura, FPS, cores) ficam em `config`. Resolução base 1280×720, 60 FPS.
- **Caminhos** de arquivos sempre relativos ao arquivo do código (`Path(__file__)`), e não à pasta onde o jogo foi aberto.
- **Imagens:** carregar com `convert_alpha()` e guardar em cache (não recarregar a cada quadro).
- **Fonte:** a fonte padrão do pygame pode não mostrar ∧, ∨, ¬, → e ↔. Usar uma TTF livre que tenha esses símbolos (por exemplo DejaVu Sans) em `assets/fontes`, e testar uma pergunta com todos eles. Implementar a quebra de linha de enunciados longos dentro de uma caixa. Salvar os JSON em UTF-8.
- **Tela de pergunta:** escolher com as setas ou teclas **1 a 4**, confirmar com Enter. Acerto em **verde**, erro em **vermelho**. Depois de um erro, mostrar a explicação da resposta certa antes da próxima pergunta.
- **Movimentação na exploração (S0):** `W`, `A`, `S`, `D` ou setas, com `dt` (tarefa c41, seção 3.10).
- **Estados:** seguir a máquina de estados da seção 2.7 (S0 a S6 adaptados), mais MENU e VITÓRIA. Criar funções simples de transição (`proximo_estado(estado, evento)`), sem criar estados que ainda não serão usados.
- **Usar retângulos, textos e barras provisórias** até o gameplay estar validado. Arte não bloqueia a programação.

---

## 8. Arte e recursos

- **Estilo:** desenho 2D com contorno escuro (#14101c), gradientes radiais e vinheta. PNG com fundo transparente para personagens.
- **Artes já geradas** (SVG gerado por Python, convertido em PNG pelo Chromium/Playwright) e enviadas ao usuário, para **1280×720**:

| Arquivo | Tamanho |
|---|---|
| `jogador_exterminador.png` | 256×320 |
| `chefe_lobisomem.png`, `chefe_frankenstein.png`, `chefe_musashi.png` | 384×448 |
| `chefe_dracula.png` | 448×512 |
| `fundo_andar1.png` a `fundo_andar4.png` | 1280×720 |
| `fundo_entrada_mansao.png` (menu inicial) | 1280×720 |

- **Padrão visual (corrigido em 09/11/2026):** o usuário pediu o estilo da versão antiga, ou seja, **desenho plano**, contorno escuro, brilhos suaves, **sem granulado, sem vinheta e sem personagem "chibi"** (cabeça grande). Vale para tudo que for novo.
- **Dimensões dos sprites (09/11/2026):** o Exterminador de frente e o de costas têm **256×320 px, 276 px de altura, pés alinhados em y≈298**. A escolha foi a proporção do de costas. Os chefes continuam como estão, por escolha do usuário.
- **Artes da exploração (09/11/2026)**, em `exploracao/` (cenas completas) e `exploracao/fundos/` (fundos sem personagem e Exterminador separado):

| Arquivo | Conteúdo |
|---|---|
| `exploracao_1_entrada.png` e `exploracao_1_entrada_botao.png` | entrada da mansão (a original do usuário, sem e com o botão COMEÇAR) |
| `exploracao_2_porta.png`, `exploracao_3_salao.png`, `exploracao_4_escada.png` | as outras 3 cenas, com o Exterminador |
| `fundos/fundo_exploracao_2_porta.png`, `fundo_exploracao_3_salao.png`, `fundo_exploracao_4_escada.png` | os mesmos cenários sem personagem (1280×720) |
| `fundos/jogador_exterminador_costas.png` e `jogador_exterminador_frente.png` | o Exterminador separado (256×320, fundo transparente) |

- **Risadas dos personagens (10/11/2026):** como a interação do jogo é em texto, o usuário pediu a voz de cada personagem como **risada**: Exterminador (homem normal), Frankenstein (zumbindo, como zumbi), Lobisomem (bem grossa, lobo mau), Musashi/fantasma (ecoada e malévola) e Drácula (homem, bem malévolo, "nhe hehehe" ou algo assim). Arquivos `sons/risada_exterminador`, `risada_frankenstein`, `risada_lobisomem`, `risada_musashi` e `risada_dracula`, em `.wav` e `.ogg` (sugestão de pasta no jogo: `assets/sons/`). A **versão 1** (síntese manual) foi reprovada pelo usuário; a **versão 2** usa a voz neural Piper "ryan" (modelo `en_US-ryan-medium`, via `sherpa-onnx`) com efeitos de tom, eco e distorção. A v2 **ainda não foi avaliada** pelo usuário. A voz Piper tem licença própria: **anotar fonte e licença** nos créditos se for usada no jogo.
- **Pendente:** os sons (acerto, erro, vitória, game over). Os inimigos secundários saíram do planejamento, então não precisam de arte. Se a troca de arma por andar (3.9) for aprovada, falta arte do Exterminador por andar.
- O usuário ainda não respondeu se quer mudanças nos cenários e na entrada da mansão.
- Qualquer recurso de terceiros (imagem, som, fonte) deve ter **fonte e licença anotadas** para os créditos do README.

---

## 9. Cronograma de código (5 etapas, 4 a 22/11/2026)

- **Total:** 36 tarefas, 57 h de trabalho (soma de horas por pessoa, guia e não medida exata). Algumas tarefas ocorrem em paralelo. Em 16/11/2026 foi acrescentada a **c41** (2 h), e nada mais mudou no cronograma.
- As **tarefas c1 a c4 já estão concluídas** (repositório e ambiente, divisão de tarefas, pastas e arquivos vazios, `main.py` com janela e laço principal).
- **Situação em 16/11/2026** (segundo o vídeo de 10/11 e o resumo do Claude Code de 15/11; ✔ = código relatado como pronto, **ainda sem commit, revisão e merge**, então pela regra 9.1 não conta como concluída; ◐ = parcial): c7 ✔, c8 ✔, c9 ✔, c22 ✔, c23 ✔, c24 ✔ (falta confirmar o teste de vida nunca negativa e a saída do pytest), c25 ✔ (revisão das alternativas e explicações pendente), c34 ✔, c26 ✔, c35 ✔ (conferir se as artes estão em `assets/imagens`), c10 ✔, c13 ✔, c31 ✔, c32 ✔, c36 ✔ (adiantada, mas será adaptada pela c41), **c39 ◐** (falta o teste real do duelo). As datas das etapas 1 a 3 já passaram.
- Tarefas marcadas **(opcional)** só entram se o jogo principal estiver funcionando.

**Etapa 1 · Projeto base e janela (4–6 nov)**
- c1 repositório e ambiente (1 h) ✔ · c2 dividir tarefas (0,5 h) ✔ · c3 pastas e arquivos vazios (1 h) ✔ · c4 `main.py` com janela e laço a 60 FPS (2 h) ✔
- c37 alinhar a versão atual do jogo (0,5 h) — **usar a seção 3 deste arquivo**
- c31 resolução 1280×720, 60 FPS, SCALED|RESIZABLE, F11 (1,5 h)
- c32 pastas de assets e carregador de imagens com cache (1,5 h)
- c38 primeira integração (0,5 h)

**Etapa 2 · Regras do jogo em código (7–10 nov)**
- c7 enum de estados (1,5 h), com a máquina de estados alterada pela equipe
- c8 `proximo_estado(estado, evento)` (1,5 h)
- c9 testes da máquina de estados com pytest (1 h)
- c33 padrão visual e tamanho dos sprites (1 h)

**Etapa 3 · Combate e perguntas (11–14 nov)** — a mais pesada, cerca de 18,5 h
- c22 formato das perguntas e vidas dos chefes (1 h)
- c23 motor de duelo em `regras.py` (2,5 h)
- c24 testes do motor e do tamanho do banco (1 h)
- c25 perguntas dos andares 1 e 2 (2,5 h)
- c34 fonte com símbolos lógicos e quebra de linha (1,5 h)
- c26 tela de pergunta (2 h)
- c35 incorporar as artes do Exterminador e dos andares 1 e 2 (1 h)
- c10 tela de combate (2,5 h)
- c13 ligar o duelo à máquina de estados (2 h)
- c39 integrar e testar o primeiro duelo contra o Lobisomem (2,5 h)

**Etapa 4 · Chefes e andares (15–18 nov)**
- c14 os 4 chefes em `chefes.py` (3 h)
- c27 perguntas dos andares 3 e 4 (3,5 h)
- c29 sequência de acertos (1,5 h, opcional)
- c15 progressão entre andares (1,5 h)
- c36 tela de exploração do andar, estado S0 (2 h)
- **c41 movimentação do Exterminador na exploração com W, A, S, D ou setas (2 h, acrescentada em 16/11/2026)** — ver seção 3.10
- c17 incorporar as artes dos andares 3 e 4 e conseguir os sons (1,5 h)
- c40 integração geral da progressão (1 h)

**Etapa 5 · Acabamento e entrega (19–22 nov)**
- c18 telas de game over, vitória e menu inicial, usando `fundo_entrada_mansao.png` (1,5 h)
- c30 dica por andar (1,5 h, opcional)
- c28 ajustar dificuldade jogando (1,5 h)
- c19 partida completa do 1º andar ao Drácula, mais teste em um segundo computador (2,5 h)
- c20 limpar o código e rodar o pytest (1 h)
- c21 README e demonstração (1 h)

### 9.1 Regras de trabalho e integração

- Cada pessoa trabalha em uma branch própria ou de funcionalidade; a branch principal deve permanecer executável.
- Uma tarefa só está concluída quando o código foi enviado, revisado, integrado e executado junto com o resto do jogo.
- Integração curta ao final de cada etapa e sempre que um módulo essencial ficar pronto. Não acumular tudo para a última etapa.
- Antes do merge: o projeto abre, a funcionalidade funciona e nada já integrado quebrou. Conflitos são resolvidos com o responsável pela integração.

### 9.2 Escopo protegido

Não desenvolver inicialmente menus de equipamentos e ações, inventário complexo, mapa livre, movimentação elaborada ou efeitos gráficos avançados. Só entram se o jogo principal estiver funcionando.

Exceção pedida pela equipe em 16/11/2026: a **c41** (movimento simples com W, A, S, D ou setas na exploração) entra no escopo. "Movimentação elaborada", mapa livre e colisão com paredes continuam fora.

### 9.3 Ordem de corte se o prazo apertar

Cortar primeiro as melhorias opcionais (dicas, sequência de acertos, sons extras e efeitos). **Nunca** cortar o fluxo principal de combate, a integração e os testes.

### 9.4 Checklist mínimo para considerar o jogo pronto

- A janela abre e fecha corretamente.
- O jogador consegue iniciar e reiniciar uma partida.
- As perguntas aparecem com alternativas legíveis e resposta correta validada.
- Acerto e erro atualizam as vidas conforme as regras acordadas (seção 3).
- Os quatro chefes e andares podem ser concluídos em sequência.
- Game over e vitória funcionam.
- As perguntas e explicações foram revisadas.
- O jogo completo foi testado por todos os integrantes.
- O README explica como instalar e executar, e os créditos e licenças estão registrados.

---

## 10. Divisão sugerida da equipe (5 integrantes)

Sugestão, ainda não confirmada pela equipe:

1. **Coordenação e integração:** repositório e estrutura, `main.py`, fluxo de estados, integração dos módulos. Também programa.
2. **Regras e duelo:** avaliação das respostas, vidas, motor de duelo, máquina de estados e testes das regras.
3. **Chefes, perguntas e progressão:** os quatro chefes, banco de perguntas com a equipe e passagem entre andares.
4. **Interface:** janela e telas, seleção de alternativas, corações na tela.
5. **Arte e recursos:** incorporar artes e sons, anotar fonte e licença.

A produção e a revisão das perguntas são de todos, com uma pessoa consolidando o formato e evitando duplicações.

---

## 11. Histórico e contexto adicional

- O cronograma original era de 5 semanas (5 out a 8 nov). Em 04/11 a equipe informou entrega em **22/11**, e as fases viraram "etapas" de 3 a 4 dias.
- Um cronograma de outra IA (`Cronograma_Revisado_Mansion_of_Logic.docx`) foi analisado e as partes boas foram incorporadas: regras de integração, escopo protegido, critério de conclusão, checklist mínimo e ordem de corte, além das tarefas de integração (c37 a c40). Foi corrigido nele: resolução 960×540 → 1280×720, divisão para 4 pessoas → 5, e estados passam a seguir os S0–S6 do relatório com MENU e VITÓRIA acrescentados. A conversa do ChatGPT em si não pôde ser lida.
- Decisões anteriores já tomadas: (substituído em 08/11/2026: menus c11 e c12 foram **retirados**); artes c35 e c17 reduzidas para "incorporar" as imagens já geradas; game over volta ao andar 1; todas as perguntas vêm da Lista Extra, partes 1 a 5.
- **16/11/2026:** a equipe pediu que, na exploração, o jogador use `W`, `A`, `S`, `D` ou as setas para movimentar o Exterminador. Foi acrescentada **só** a tarefa c41 ao cronograma (versão 16). O texto da c36 não foi alterado e conflita com a c41 (seção 3.10).
- **15/11/2026:** foi montado o prompt da Etapa 3 para o Claude Code. Segundo o resumo dele, as tarefas c22 a c26, c34, c35, c10 e c13 foram feitas (a c39 parcial), a exploração (c36) foi adiantada a pedido da equipe, `questoes.py` virou arquivo separado, a pergunta 89 saiu do andar 2 e `.gitignore` e as fontes foram criados (seção 6.3). Os pontos que faltam estão em 3.4 (itens 6 a 8) e 6.3.
- **10/11/2026:** revisão do vídeo do código da equipe. Máquina de estados feita (c7 e c8), testes da máquina (c9) ainda pendentes na época, JSON dos 4 andares já escritos, andar 2 com 8 perguntas, enunciados 13, 41 e 47 do andar 4 alterados, e o comentário antigo em `chefes.py` falando das variáveis removidas. Também foram geradas as risadas dos personagens (seção 8).
- **09/11/2026:** a equipe confirmou: o jogo é simples (acerto tira 1 coração do chefe, erro tira 1 do Exterminador), a tabela-verdade de D1 (2.4) também saiu, a coluna de temática da 2.1 fica por causa da ideia de troca automática de arma por andar (em análise, seção 3.9) e os inimigos secundários saíram do planejamento (tarefa c16 retirada).
- **08/11/2026:** a equipe decidiu alterar o relatório. Saíram do jogo as variáveis (2.2), as condições de dano D1–D4 (2.3), DNF/CNF (2.5) e SAT (2.6), e a máquina de estados (2.7) foi modificada. Foram retiradas do cronograma as tarefas c5, c6, c11 e c12. A regra "o cronograma não altera o relatório" ficou restrita a esses itens: o resto do relatório não mudou.