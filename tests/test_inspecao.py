import math
import random

import pytest

from controle import ModuloControle
from gerador import gerar_produtos
from inspecao import ModuloInspecao, inspecao_tipo1, inspecao_tipo2, merge_sort


@pytest.mark.parametrize("n,esperado", [(1, 1), (2, 2), (3, 2), (4, 3), (10, 4), (10_000, 14)])
def test_tipo1_exemplos(n, esperado):
    assert inspecao_tipo1(n) == esperado


def test_tipo1_forma_fechada():
    for n in range(1, 5000):
        assert inspecao_tipo1(n) == math.floor(math.log2(n)) + 1


def test_tipo2_forma_fechada():
    for n in range(1, 2000):
        assert inspecao_tipo2(n) == n * (n + 1) // 2


@pytest.mark.parametrize("funcao", [inspecao_tipo1, inspecao_tipo2])
def test_tamanho_invalido(funcao):
    with pytest.raises(ValueError):
        funcao(0)


def test_merge_sort_ordena_e_e_estavel():
    rng = random.Random(0)
    pares = [(rng.randint(0, 20), i) for i in range(500)]
    assert merge_sort(pares, chave=lambda p: p[0]) == sorted(pares, key=lambda p: p[0])
    assert merge_sort([], chave=lambda x: x) == []


def test_modulo_retorna_lista_ordenada_e_envia_ao_controle():
    produtos = gerar_produtos(300, seed=5)
    controle = ModuloControle()
    lista = ModuloInspecao().processar(produtos, controle, exibir=False)
    tempos = [p.tempo_inspecao for p in lista]
    assert tempos == sorted(tempos)
    assert len(lista) == len(produtos)
    assert controle.tabela is not None and controle.tabela.n > 0
