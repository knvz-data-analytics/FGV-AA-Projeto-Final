"""

Módulo de controle (Tarefa 5)

O estoque é dividido em m tipos de clientes, com m < k (k = quantidade de chaves de cliente distintas)

Isso é modelado como uma tabela hash com m posições, função de dispersão pelo método da divisão (h(k) = k mod m) e tratamento de colisões por encadeamento separado

"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, Sequence

from gerador import Consulta
from interface import formatar_horas, formatar_tabela

if TYPE_CHECKING:
    from inspecao import ProdutoInspecionado
    from monitoramento import Monitor

MENSAGEM_NAO_ENCONTRADO = "Produto não encontrado"
FATOR_CARGA_ALVO = 4


@dataclass(frozen=True)
class Registro:
    """Informação armazenada no estoque para uma chave de cliente."""

    chave_cliente: int
    tipo: int
    tamanho: int
    tempo_inspecao: int


@dataclass(frozen=True)
class ResultadoBusca:
    consulta: Consulta
    registro: Registro | None

    @property
    def encontrado(self) -> bool:
        return self.registro is not None

    @property
    def mensagem(self) -> str:
        if self.registro is None:
            return MENSAGEM_NAO_ENCONTRADO
        return f"{formatar_horas(self.registro.tempo_inspecao)} h"


def eh_primo(x: int) -> bool:
    if x < 2:
        return False
    if x % 2 == 0:
        return x == 2
    divisor = 3
    while divisor * divisor <= x:
        if x % divisor == 0:
            return False
        divisor += 2
    return True


def maior_primo_ate(x: int) -> int:
    """Maior primo <= x (x >= 2)."""
    while not eh_primo(x):
        x -= 1
    return x


def escolher_m(k: int, n: int, fator_carga: int = FATOR_CARGA_ALVO) -> int:
    """Escolhe a quantidade m de tipos de clientes (tamanho da tabela).

    Regras: m < k (exigência do enunciado) e m próximo de n / fator_carga,
    para que cada tipo de cliente guarde em média ~fator_carga produtos.
    Usa um número primo, o que espalha melhor as chaves no método da divisão.
    """
    alvo = min(k - 1, max(2, n // fator_carga))
    if alvo < 2:
        return 1
    return maior_primo_ate(alvo)


class TabelaHash:
    """Tabela hash com encadeamento separado.

    Inserção e busca custam O(1 + α) em média, onde α = n / m é o fator de
    carga. ``comparacoes`` acumula quantos registros foram examinados nas
    buscas, métrica usada pelo módulo de monitoramento.
    """

    def __init__(self, m: int) -> None:
        if m < 1:
            raise ValueError("A tabela precisa de ao menos 1 posição")
        self.m = m
        self._baldes: list[list[Registro]] = [[] for _ in range(m)]
        self.n = 0
        self.comparacoes = 0

    def indice(self, chave_cliente: int) -> int:
        """Função hash pelo método da divisão: tipo de cliente da chave."""
        return chave_cliente % self.m

    def inserir(self, registro: Registro) -> bool:
        """Insere o registro no tipo de cliente correspondente.

        Retorna False se o registro idêntico já estava armazenado.
        """
        balde = self._baldes[self.indice(registro.chave_cliente)]
        if registro in balde:
            return False
        balde.append(registro)
        self.n += 1
        return True

    def buscar(self, chave_cliente: int, tamanho: int) -> Registro | None:
        """Busca o produto de ``tamanho`` para a ``chave_cliente``.

        Se a mesma chave tiver mais de um produto com esse tamanho (tipos
        diferentes), retorna o primeiro inserido.
        """
        for registro in self._baldes[self.indice(chave_cliente)]:
            self.comparacoes += 1
            if registro.chave_cliente == chave_cliente and registro.tamanho == tamanho:
                return registro
        return None

    @property
    def fator_carga(self) -> float:
        return self.n / self.m

    def estatisticas(self) -> dict[str, float]:
        tamanhos = [len(b) for b in self._baldes]
        return {
            "m": self.m,
            "n": self.n,
            "fator_carga": self.fator_carga,
            "maior_balde": max(tamanhos),
            "baldes_vazios": sum(1 for t in tamanhos if t == 0),
        }


class ModuloControle:
    """Executa as operações de inserção e busca no estoque."""

    def __init__(self, m: int | None = None, monitor: Monitor | None = None) -> None:
        self._m_fixo = m
        self.monitor = monitor
        self.tabela: TabelaHash | None = None

    def receber(self, inspecionados: Sequence[ProdutoInspecionado]) -> None:
        """Inserção: armazena (tipo, tamanho, tempo) por tipo de cliente."""
        if not inspecionados:
            return
        if self.tabela is None:
            k = len({p.chave_cliente for p in inspecionados})
            if self._m_fixo is not None:
                if k >= 2 and not 1 <= self._m_fixo < k:
                    raise ValueError(f"m deve ser menor que k: m={self._m_fixo}, k={k}")
                m = self._m_fixo
            else:
                m = escolher_m(k, len(inspecionados))
            self.tabela = TabelaHash(m)

        inicio = time.perf_counter()
        for p in inspecionados:
            self.tabela.inserir(Registro(p.chave_cliente, p.tipo, p.tamanho, p.tempo_inspecao))
        duracao = time.perf_counter() - inicio

        if self.monitor is not None:
            self.monitor.registrar(
                modulo="controle_insercao",
                quantidade=len(inspecionados),
                tamanho_medio=sum(p.tamanho for p in inspecionados) / len(inspecionados),
                tempo_s=duracao,
                metrica=self.tabela.fator_carga,
            )

    def buscar(self, consultas: Sequence[Consulta]) -> list[ResultadoBusca]:
        """Busca: retorna o tempo de inspeção ou 'Produto não encontrado'."""
        if self.tabela is None:
            return [ResultadoBusca(c, None) for c in consultas]

        comparacoes_antes = self.tabela.comparacoes
        inicio = time.perf_counter()
        resultados = [ResultadoBusca(c, self.tabela.buscar(c.chave_cliente, c.tamanho)) for c in consultas]
        duracao = time.perf_counter() - inicio

        if self.monitor is not None and consultas:
            self.monitor.registrar(
                modulo="controle_busca",
                quantidade=len(consultas),
                tamanho_medio=sum(c.tamanho for c in consultas) / len(consultas),
                tempo_s=duracao,
                metrica=(self.tabela.comparacoes - comparacoes_antes) / len(consultas),
            )
        return resultados

    @staticmethod
    def exibir_resultados(resultados: Sequence[ResultadoBusca], limite: int | None = 20) -> None:
        print("\n=== Resultado das buscas ===")
        encontrados = sum(1 for r in resultados if r.encontrado)
        print(f"{len(resultados)} buscas | {encontrados} encontradas | {len(resultados) - encontrados} não encontradas")
        linhas = [
            (i, r.consulta.chave_cliente, r.consulta.tamanho, r.mensagem)
            for i, r in enumerate(resultados, start=1)
        ]
        print(formatar_tabela(("#", "Chave cliente", "Tamanho", "Tempo de inspeção"), linhas, limite))