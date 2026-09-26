# Sistema de Controle de Estoque Industrial

Projeto final da disciplina: implementação e simulação de um sistema que controla o estoque de produtos de uma indústria, aplicando conceitos de análise de algoritmos, ordenação e estruturas de dados (tabelas hash).

## Visão geral

O sistema é composto por três módulos que trabalham em sequência:

```
┌────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│    Gerador     │ ──▶ │ Módulo de        │ ──▶ │ Módulo de        │
│   de entradas  │     │ Inspeção         │     │ Controle         │
└────────────────┘     └──────────────────┘     └──────────────────┘
                               │                         │
                               └──────────┬──────────────┘
                                          ▼
                               ┌──────────────────┐
                               │ Módulo de        │
                               │ Monitoramento    │
                               └──────────────────┘
```

| Módulo | Entrada | Responsabilidade |
|---|---|---|
| Inspeção | chave do cliente, tipo do produto, tamanho do produto | Calcula o tempo de inspeção de cada produto, ordena e exibe a lista |
| Controle | chave do cliente, tipo do produto, tempo de inspeção | Insere e busca produtos no estoque |
| Monitoramento | métricas de execução dos outros módulos | Exibe gráficos com o histórico de eficiência computacional |

## Módulo de Inspeção

O tempo de inspeção depende do tipo do produto e do seu tamanho `n`.

### Produto tipo 1

O produto de tamanho `n` é preparado e inspecionado; em seguida, é dividido ao meio (divisão inteira) e a metade é inspecionada, gastando 1 h por etapa. O processo se repete até `n = 1`, que também leva 1 h.

Recorrência:

```
T(1) = 1
T(n) = T(⌊n/2⌋) + 1
```

Complexidade: **O(log n)**.

### Produto tipo 2

O produto de tamanho `n` é inspecionado em `n` horas; retira-se 1 unidade e o novo tamanho é inspecionado em `n − 1` horas, e assim por diante até `n = 1` (1 h).

```
T(n) = n + (n − 1) + ... + 1 = n(n + 1) / 2
```

Complexidade: **O(n²)**.

### Operações do módulo

1. Recebe uma lista de produtos dos tipos 1 e 2 com tamanhos variados.
2. Calcula o tempo de inspeção de cada produto.
3. Retorna a lista de produtos processados **ordenada pelo tempo de inspeção**.
4. Exibe a lista ordenada na tela.
5. Envia a lista de produtos inspecionados ao módulo de controle.

## Módulo de Controle

O estoque é dividido em `m` tipos de clientes, sendo `m` sempre menor que a quantidade `k` de chaves de clientes processadas (`m < k`). Isso caracteriza naturalmente uma **tabela hash** com `m` posições, em que várias chaves de cliente são mapeadas para o mesmo tipo e as colisões precisam ser tratadas.

### Inserção

Para cada tipo de cliente, armazena a tripla recebida do módulo de inspeção:

```
(tipo do produto, tamanho do produto, tempo de inspeção)
```

### Busca

Recebe uma lista de duplas `(chave do cliente, tamanho do produto)` e, para cada uma:

- retorna o **tempo de inspeção** do produto, se o tamanho for encontrado para aquela chave de cliente;
- exibe **"Produto não encontrado"**, caso contrário.

## Módulo de Monitoramento

Acompanha o desempenho do processamento das listas e exibe o histórico da eficiência computacional em três gráficos:

1. Desempenho do módulo de inspeção para produtos do **tipo 1**.
2. Desempenho do módulo de inspeção para produtos do **tipo 2**.
3. Desempenho do **módulo de controle** (inserção e busca).

## Simulação

O sistema é avaliado por simulação, escalonando a quantidade e o tamanho dos produtos processados:

| Parâmetro | Faixa mínima |
|---|---|
| Quantidade de produtos por lista | 10 a 10.000 |
| Tamanho dos produtos | 10 a 10.000 |
| Tipos de produto | 1 e 2 |

Faixas maiores podem ser usadas nas simulações. Para cada simulação, o sistema deve exibir a lista de dados fornecida como entrada.

## Etapas de desenvolvimento

- [ ] **1. Arquitetura** — definir a estrutura geral do sistema e como a simulação será realizada (fluxogramas ou arquitetura básica).
- [ ] **2. Gerador de dados** — implementar o gerador de entradas, a interface de recebimento pelo módulo de inspeção e a interface que exibe a lista fornecida em cada simulação.
- [ ] **3. Módulo de inspeção** — implementar o cálculo dos tempos, a ordenação e o envio ao controle.
- [ ] **4. Monitoramento da inspeção** — executar simulações do módulo de inspeção com diferentes entradas e exibir os gráficos de desempenho.
- [ ] **5. Módulo de controle** — implementar inserção e busca no estoque.
- [ ] **6. Monitoramento do controle** — executar simulações completas do sistema e exibir os gráficos de desempenho de inspeção e controle.

## Estrutura sugerida do repositório

```
.
├── README.md
├── docs/
│   └── arquitetura.md        # fluxogramas e decisões de projeto
├── src/
│   ├── gerador.py            # geração das listas de entrada
│   ├── inspecao.py           # módulo de inspeção
│   ├── controle.py           # módulo de controle (tabela hash)
│   ├── monitoramento.py      # coleta de métricas e gráficos
│   └── main.py               # orquestra a simulação
└── resultados/               # gráficos gerados
```

## Como executar

```bash
# instalar dependências
pip install -r requirements.txt

# rodar a simulação completa
python src/main.py
```

> Ajuste os comandos conforme a implementação final.
