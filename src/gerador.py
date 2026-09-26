"""
Geração e recebimento dos dados de entrada do sistema (Tarefa 2)

Define as estruturas de entrada (Produto e Consulta), o gerador aleatório de listas de produtos e de consultas, e a interface de leitura/escrita em CSV usada para fornecer dados ao módulo de inspeção.

"""
from __future__ import annotations

import csv
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

TIPOS_VALIDOS = (1, 2)
TAMANHO_MIN_PADRAO = 10
TAMANHO_MAX_PADRAO = 10_000
CAMPOS_CSV = ("chave_cliente", "tipo", "tamanho")


@dataclass(frozen=True)
class Produto:
    """Produto recebido pelo módulo de inspeção."""

    chave_cliente: int
    tipo: int
    tamanho: int


@dataclass(frozen=True)
class Consulta:
    """Dupla (chave do cliente, tamanho do produto) usada na busca."""

    chave_cliente: int
    tamanho: int


def validar_produto(produto: Produto) -> Produto:
    """Garante que o produto respeita as regras do sistema."""
    if produto.tipo not in TIPOS_VALIDOS:
        raise ValueError(f"Tipo de produto inválido: {produto.tipo} (esperado 1 ou 2)")
    if produto.tamanho < 1:
        raise ValueError(f"Tamanho inválido: {produto.tamanho} (deve ser >= 1)")
    if produto.chave_cliente < 0:
        raise ValueError(f"Chave de cliente inválida: {produto.chave_cliente} (deve ser >= 0)")
    return produto


def gerar_produtos(
    quantidade: int,
    tamanho_min: int = TAMANHO_MIN_PADRAO,
    tamanho_max: int = TAMANHO_MAX_PADRAO,
    proporcao_tipo1: float = 0.5,
    max_chave: int | None = None,
    seed: int | None = None,
) -> list[Produto]:
    """Gera uma lista aleatória de produtos.

    As chaves de cliente são sorteadas em [1, max_chave]; por padrão
    max_chave = 2 * quantidade, o que produz chaves repetidas (um mesmo
    cliente com vários produtos), como acontece em um estoque real.
    """
    if quantidade < 1:
        raise ValueError("A quantidade de produtos deve ser >= 1")
    if not 1 <= tamanho_min <= tamanho_max:
        raise ValueError("Faixa de tamanhos inválida: exige 1 <= tamanho_min <= tamanho_max")
    if not 0.0 <= proporcao_tipo1 <= 1.0:
        raise ValueError("proporcao_tipo1 deve estar entre 0 e 1")

    rng = random.Random(seed)
    if max_chave is None:
        max_chave = max(10, 2 * quantidade)

    produtos = []
    for _ in range(quantidade):
        tipo = 1 if rng.random() < proporcao_tipo1 else 2
        produtos.append(
            Produto(
                chave_cliente=rng.randint(1, max_chave),
                tipo=tipo,
                tamanho=rng.randint(tamanho_min, tamanho_max),
            )
        )
    return produtos


def gerar_consultas(
    produtos: Sequence[Produto],
    quantidade: int,
    taxa_acerto: float = 0.8,
    seed: int | None = None,
) -> list[Consulta]:
    """Gera consultas de busca a partir de uma lista de produtos.

    Uma fração ``taxa_acerto`` das consultas aponta para produtos existentes;
    as demais usam chaves fora do intervalo gerado, garantindo o caso
    "Produto não encontrado".
    """
    if not produtos:
        raise ValueError("É preciso ao menos um produto para gerar consultas")
    if not 0.0 <= taxa_acerto <= 1.0:
        raise ValueError("taxa_acerto deve estar entre 0 e 1")

    rng = random.Random(seed)
    maior_chave = max(p.chave_cliente for p in produtos)
    maior_tamanho = max(p.tamanho for p in produtos)

    consultas = []
    for _ in range(quantidade):
        if rng.random() < taxa_acerto:
            alvo = rng.choice(produtos)
            consultas.append(Consulta(alvo.chave_cliente, alvo.tamanho))
        else:
            chave_inexistente = rng.randint(maior_chave + 1, 2 * maior_chave + 1)
            consultas.append(Consulta(chave_inexistente, rng.randint(1, maior_tamanho)))
    return consultas


def salvar_produtos_csv(produtos: Sequence[Produto], caminho: str | Path) -> Path:
    """Salva uma lista de produtos em CSV (chave_cliente, tipo, tamanho)."""
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(CAMPOS_CSV)
        for p in produtos:
            escritor.writerow((p.chave_cliente, p.tipo, p.tamanho))
    return caminho


def carregar_produtos_csv(caminho: str | Path) -> list[Produto]:
    """Interface de recebimento: lê e valida produtos de um arquivo CSV."""
    caminho = Path(caminho)
    produtos = []
    with caminho.open(newline="", encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)
        faltando = set(CAMPOS_CSV) - set(leitor.fieldnames or ())
        if faltando:
            raise ValueError(f"CSV sem as colunas obrigatórias: {', '.join(sorted(faltando))}")
        for numero_linha, linha in enumerate(leitor, start=2):
            try:
                produto = Produto(
                    chave_cliente=int(linha["chave_cliente"]),
                    tipo=int(linha["tipo"]),
                    tamanho=int(linha["tamanho"]),
                )
                produtos.append(validar_produto(produto))
            except (TypeError, ValueError) as erro:
                raise ValueError(f"{caminho}, linha {numero_linha}: {erro}") from erro
    if not produtos:
        raise ValueError(f"{caminho} não contém produtos")
    return produtos