"""

Módulo de inspeção (Tarefa 3)

Calcula o tempo de inspeção de cada produto, ordena a lista pelo tempo de inspeção (merge sort), exibe a lista ordenada e a envia ao módulo de controle.

"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, Sequence, TypeVar

from gerador import Produto
from interface import formatar_horas, formatar_tabela

if TYPE_CHECKING:  # evita import circular em tempo de execução
    from controle import ModuloControle
    from monitoramento import Monitor

T = TypeVar("T")


@dataclass(frozen=True)
class ProdutoInspecionado:
    """Produto com o tempo de inspeção (em horas) já calculado."""

    chave_cliente: int
    tipo: int
    tamanho: int
    tempo_inspecao: int


def inspecao_tipo1(n: int) -> int:
    """Tempo de inspeção de um produto tipo 1 de tamanho n.

    Gasta 1 h no tamanho n; divide ao meio (divisão inteira) e gasta mais 1 h
    no novo tamanho, até chegar a n = 1 (também 1 h).

        T(1) = 1
        T(n) = T(n // 2) + 1   =>   T(n) = floor(log2 n) + 1

    O laço executa floor(log2 n) + 1 iterações: complexidade O(log n).
    """
    if n < 1:
        raise ValueError("O tamanho do produto deve ser >= 1")
    horas = 0
    tamanho = n
    while tamanho > 1:
        horas += 1  # inspeciona o tamanho atual
        tamanho //= 2  # divide ao meio (resultado inteiro)
    return horas + 1  # inspeção final com tamanho 1


def inspecao_tipo2(n: int) -> int:
    """Tempo de inspeção de um produto tipo 2 de tamanho n.

    Gasta n horas no tamanho n; retira 1 unidade e gasta n - 1 horas, e assim
    por diante até n = 1 (1 h).

        T(1) = 1
        T(n) = T(n - 1) + n   =>   T(n) = n(n + 1) / 2 horas   (Θ(n²) horas)

    O laço executa n iterações: complexidade computacional O(n).
    A versão iterativa evita estourar o limite de recursão do Python
    (n chega a 10.000 nas simulações e o limite padrão é 1.000).
    """
    if n < 1:
        raise ValueError("O tamanho do produto deve ser >= 1")
    horas = 0
    tamanho = n
    while tamanho >= 1:
        horas += tamanho
        tamanho -= 1  # retira 1 unidade de medida
    return horas


INSPECOES: dict[int, Callable[[int], int]] = {1: inspecao_tipo1, 2: inspecao_tipo2}


def merge_sort(itens: Sequence[T], chave: Callable[[T], object]) -> list[T]:
    """Merge sort estável: O(n log n) em qualquer caso.

    Escolhido por garantir O(n log n) mesmo no pior caso e por ser estável
    (produtos com o mesmo tempo mantêm a ordem relativa).
    """
    if len(itens) <= 1:
        return list(itens)
    meio = len(itens) // 2
    esquerda = merge_sort(itens[:meio], chave)
    direita = merge_sort(itens[meio:], chave)

    resultado: list[T] = []
    i = j = 0
    while i < len(esquerda) and j < len(direita):
        if chave(esquerda[i]) <= chave(direita[j]):  # <= garante estabilidade
            resultado.append(esquerda[i])
            i += 1
        else:
            resultado.append(direita[j])
            j += 1
    resultado.extend(esquerda[i:])
    resultado.extend(direita[j:])
    return resultado


class ModuloInspecao:
    """Recebe produtos, calcula os tempos de inspeção e ordena o resultado."""

    def __init__(self, monitor: Monitor | None = None) -> None:
        self.monitor = monitor

    def inspecionar(self, produtos: Sequence[Produto]) -> list[ProdutoInspecionado]:
        """Retorna os produtos inspecionados ordenados pelo tempo de inspeção."""
        inspecionados: list[ProdutoInspecionado] = []

        for tipo, calcular_tempo in INSPECOES.items():
            do_tipo = [p for p in produtos if p.tipo == tipo]
            if not do_tipo:
                continue
            inicio = time.perf_counter()
            resultado = [
                ProdutoInspecionado(p.chave_cliente, p.tipo, p.tamanho, calcular_tempo(p.tamanho))
                for p in do_tipo
            ]
            duracao = time.perf_counter() - inicio
            inspecionados.extend(resultado)

            if self.monitor is not None:
                self.monitor.registrar(
                    modulo=f"inspecao_tipo{tipo}",
                    quantidade=len(do_tipo),
                    tamanho_medio=sum(p.tamanho for p in do_tipo) / len(do_tipo),
                    tempo_s=duracao,
                    metrica=sum(r.tempo_inspecao for r in resultado) / len(resultado),
                )

        inicio = time.perf_counter()
        ordenados = merge_sort(inspecionados, chave=lambda p: p.tempo_inspecao)
        if self.monitor is not None and ordenados:
            self.monitor.registrar(
                modulo="inspecao_ordenacao",
                quantidade=len(ordenados),
                tamanho_medio=sum(p.tamanho for p in ordenados) / len(ordenados),
                tempo_s=time.perf_counter() - inicio,
            )
        return ordenados

    @staticmethod
    def exibir(inspecionados: Sequence[ProdutoInspecionado], limite: int | None = 20) -> None:
        """Exibe na tela a lista ordenada pelo tempo de inspeção."""
        print("\n=== Produtos inspecionados (ordenados pelo tempo de inspeção) ===")
        linhas = [
            (i, p.chave_cliente, p.tipo, p.tamanho, formatar_horas(p.tempo_inspecao))
            for i, p in enumerate(inspecionados, start=1)
        ]
        print(formatar_tabela(("#", "Chave cliente", "Tipo", "Tamanho", "Tempo (h)"), linhas, limite))

    @staticmethod
    def enviar(inspecionados: Sequence[ProdutoInspecionado], controle: ModuloControle) -> None:
        """Envia a lista de produtos inspecionados para o módulo de controle."""
        controle.receber(inspecionados)

    def processar(
        self,
        produtos: Sequence[Produto],
        controle: ModuloControle,
        exibir: bool = True,
        limite: int | None = 20,
    ) -> list[ProdutoInspecionado]:
        """Executa as três operações do módulo: ordenar, exibir e enviar."""
        ordenados = self.inspecionar(produtos)
        if exibir:
            self.exibir(ordenados, limite)
        self.enviar(ordenados, controle)
        return ordenados