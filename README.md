# Sistema de Controle de Estoque Industrial

Projeto final da disciplina: implementação e simulação de um sistema que controla o estoque de produtos de uma indústria, aplicando conceitos de análise de algoritmos, ordenação e tabelas hash.

## Visão geral

```
┌────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│    Gerador     │ ──▶ │ Módulo de        │ ──▶ │ Módulo de        │
│  de entradas   │     │ Inspeção         │     │ Controle         │
└────────────────┘     └──────────────────┘     └──────────────────┘
                               │                         │
                               └──────────┬──────────────┘
                                          ▼
                               ┌──────────────────┐
                               │ Módulo de        │
                               │ Monitoramento    │
                               └──────────────────┘
```

| Módulo | Arquivo | Responsabilidade | Complexidade |
|---|---|---|---|
| Gerador / interface | `gerador.py`, `interface.py` | Gera listas de produtos e consultas, lê/grava CSV, exibe listas | O(n) |
| Inspeção | `inspecao.py` | Calcula tempos, ordena (merge sort), exibe e envia ao controle | tipo 1: O(log n) · tipo 2: O(n) · ordenação: O(n log n) |
| Controle | `controle.py` | Inserção e busca em tabela hash com m tipos de cliente | O(1 + α) por operação |
| Monitoramento | `monitoramento.py` | Registra medições e gera os três gráficos | — |
| Simulação | `simulacao.py`, `main.py` | Escalona quantidade e tamanho dos produtos | — |

A arquitetura detalhada, os fluxogramas e as decisões de projeto estão em [`docs/arquitetura.md`](docs/arquitetura.md).

## Módulo de Inspeção

**Tipo 1.** Gasta 1 h em cada tamanho n, ⌊n/2⌋, ⌊n/4⌋, …, 1:

```
T(1) = 1,   T(n) = T(⌊n/2⌋) + 1   ⇒   T(n) = ⌊log₂ n⌋ + 1 horas   — O(log n)
```

**Tipo 2.** Gasta n horas, depois n − 1, …, até 1:

```
T(1) = 1,   T(n) = T(n − 1) + n   ⇒   T(n) = n(n + 1)/2 horas
```

O algoritmo executa n passos (custo computacional O(n)), mas o tempo de inspeção simulado cresce em Θ(n²).

Depois de calcular os tempos, o módulo ordena a lista com **merge sort** (estável, O(n log n)), exibe a lista ordenada e a envia ao módulo de controle.

## Módulo de Controle

O estoque é uma **tabela hash** com `m` posições (os tipos de cliente), com `m < k`, onde `k` é o número de chaves de cliente distintas. A função hash é `h(k) = k mod m` e as colisões são tratadas por encadeamento separado. Cada registro guarda `(tipo do produto, tamanho do produto, tempo de inspeção)`.

Se `m` não for informado, o sistema escolhe o maior primo menor que `k` e próximo de `n/4`, mantendo o fator de carga α ≈ 4.

- **Inserção:** armazena cada produto inspecionado no tipo de cliente `h(chave)`.
- **Busca:** recebe duplas `(chave do cliente, tamanho)` e retorna o tempo de inspeção ou **"Produto não encontrado"**.

## Módulo de Monitoramento

Gera três gráficos em `resultados/`:

| Arquivo | Conteúdo |
|---|---|
| `inspecao_tipo1.png` | Tempo de execução × quantidade de produtos e × tamanho n (com horas de inspeção) |
| `inspecao_tipo2.png` | Idem para o tipo 2 — evidencia O(n) passos vs. n(n+1)/2 horas |
| `controle.png` | Tempo de inserção e busca × quantidade; comparações por busca e fator de carga |

Todas as medições brutas ficam em `resultados/medicoes.csv`.

## Simulação

| Cenário | Parâmetro escalonado | Demais parâmetros |
|---|---|---|
| Quantidade | 10, 50, 100, 500, 1.000, 2.500, 5.000, 10.000 produtos | tamanhos aleatórios de 10 a 10.000 |
| Tamanho | n = 10, 50, 100, 500, 1.000, 2.500, 5.000, 10.000 | 500 produtos por lista |

Cada ponto é a média de 3 repetições (configurável), com barra de desvio padrão. A simulação completa leva poucos segundos.

## Como executar

Requer Python 3.10+.

```bash
pip install -r requirements.txt
```

**Demonstração** — uma execução completa, exibindo a lista de entrada, a lista ordenada, o estoque e as buscas:

```bash
python src/main.py demo
python src/main.py demo --quantidade 30 --consultas 15 --seed 7
python src/main.py demo --entrada entradas/lista.csv --completo
```

**Simulação completa** com gráficos:

```bash
python src/main.py simular                      # faixas de 10 a 10.000
python src/main.py simular --repeticoes 5 --mostrar
python src/main.py simular --rapido             # faixas menores, para testar
python src/main.py simular --exibir-entradas    # exibe a lista de cada rodada
```

**Gerar uma lista de entrada** em CSV (colunas `chave_cliente,tipo,tamanho`):

```bash
python src/main.py gerar --quantidade 1000 --saida entradas/lista.csv --seed 1
```

**Testes:**

```bash
python -m pytest
```

## Estrutura do repositório

```
.
├── README.md
├── requirements.txt
├── docs/
│   └── arquitetura.md        # fluxogramas e decisões de projeto
├── src/
│   ├── gerador.py            # geração e leitura das entradas
│   ├── interface.py          # exibição das listas no terminal
│   ├── inspecao.py           # módulo de inspeção
│   ├── controle.py           # módulo de controle (tabela hash)
│   ├── monitoramento.py      # medições e gráficos
│   ├── simulacao.py          # cenários de simulação
│   └── main.py               # linha de comando
├── tests/                    # testes com pytest
└── resultados/               # gráficos e medições gerados
```

## Etapas de desenvolvimento

- [x] **1. Arquitetura** — `docs/arquitetura.md`
- [x] **2. Gerador de dados e interfaces** — `gerador.py`, `interface.py`
- [x] **3. Módulo de inspeção** — `inspecao.py`
- [x] **4. Monitoramento da inspeção** — `monitoramento.py` (gráficos tipo 1 e tipo 2)
- [x] **5. Módulo de controle** — `controle.py`
- [x] **6. Monitoramento do controle** — `monitoramento.py` (gráfico do controle) e `simulacao.py`