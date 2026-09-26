"""

Simulação do sistema escalonando quantidade e tamanho dos produtos.

"""

from __future__ import annotations

import gc
from typing import Callable, Sequence

from controle import ModuloControle
from gerador import Produto, gerar_consultas, gerar_produtos
from inspecao import ModuloInspecao
from interface import exibir_produtos, resumo_produtos
from monitoramento import Monitor

QUANTIDADES = (10, 50, 100, 500, 1_000, 2_500, 5_000, 10_000)
TAMANHOS = (10, 50, 100, 500, 1_000, 2_500, 5_000, 10_000)
QUANTIDADE_FIXA = 500  # produtos por lista no cenário que escalona o tamanho

QUANTIDADES_RAPIDO = (10, 50, 100, 500, 1_000, 2_000)
TAMANHOS_RAPIDO = (10, 50, 100, 500, 1_000, 2_000)


def executar_rodada(
    produtos: Sequence[Produto],
    monitor: Monitor,
    seed: int | None = None,
    m: int | None = None,
) -> None:
    """Uma execução completa: inspeção -> controle (inserção) -> buscas."""
    inspecao = ModuloInspecao(monitor)
    controle = ModuloControle(m=m, monitor=monitor)
    inspecao.processar(produtos, controle, exibir=False)
    consultas = gerar_consultas(produtos, len(produtos), seed=seed)
    controle.buscar(consultas)


def simular(
    monitor: Monitor,
    quantidades: Sequence[int] = QUANTIDADES,
    tamanhos: Sequence[int] = TAMANHOS,
    quantidade_fixa: int = QUANTIDADE_FIXA,
    repeticoes: int = 3,
    seed: int = 42,
    exibir_entradas: bool = False,
    log: Callable[[str], None] = print,
) -> None:
    """Executa os dois cenários de simulação registrando tudo no monitor."""
    rodada = 0

    def rodar(cenario: str, parametro: int, produtos: list[Produto], rep: int) -> None:
        nonlocal rodada
        rodada += 1
        log(f"[{cenario:>10} = {parametro:>6}] rep {rep + 1}/{repeticoes} | {resumo_produtos(produtos)}")
        if exibir_entradas:
            exibir_produtos(produtos, f"Entrada — {cenario} = {parametro}, repetição {rep + 1}", limite=10)
        monitor.definir_contexto(cenario, parametro)
        gc.collect()
        gc.disable()  # evita que o coletor de lixo distorça as medições (como no timeit)
        try:
            executar_rodada(produtos, monitor, seed=seed + rodada)
        finally:
            gc.enable()

    log("\n>>> Cenário 1: escalonando a quantidade de produtos (tamanhos aleatórios de 10 a 10.000)")
    for quantidade in quantidades:
        for rep in range(repeticoes):
            produtos = gerar_produtos(quantidade, seed=seed + rodada)
            rodar("quantidade", quantidade, produtos, rep)

    log(f"\n>>> Cenário 2: escalonando o tamanho dos produtos ({quantidade_fixa} produtos por lista)")
    for tamanho in tamanhos:
        for rep in range(repeticoes):
            produtos = gerar_produtos(quantidade_fixa, tamanho_min=tamanho, tamanho_max=tamanho, seed=seed + rodada)
            rodar("tamanho", tamanho, produtos, rep)