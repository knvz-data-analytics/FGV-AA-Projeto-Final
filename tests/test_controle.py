import pytest

from controle import MENSAGEM_NAO_ENCONTRADO, ModuloControle, Registro, TabelaHash, escolher_m
from gerador import Consulta, gerar_consultas, gerar_produtos
from inspecao import ModuloInspecao, ProdutoInspecionado


def test_insercao_e_busca():
    tabela = TabelaHash(7)
    tabela.inserir(Registro(15, 1, 100, 7))
    tabela.inserir(Registro(22, 2, 100, 5050))  # 15 e 22 colidem (mod 7)
    assert tabela.buscar(22, 100).tempo_inspecao == 5050
    assert tabela.buscar(15, 100).tempo_inspecao == 7
    assert tabela.buscar(15, 99) is None


def test_insercao_duplicada_ignorada():
    tabela = TabelaHash(3)
    assert tabela.inserir(Registro(1, 1, 10, 4))
    assert not tabela.inserir(Registro(1, 1, 10, 4))
    assert tabela.n == 1


@pytest.mark.parametrize("k,n", [(2, 10), (3, 3), (50, 1000), (8000, 10_000), (10, 10)])
def test_escolher_m_menor_que_k(k, n):
    m = escolher_m(k, n)
    assert 1 <= m < k


def test_m_informado_deve_ser_menor_que_k():
    lista = [ProdutoInspecionado(c, 1, 10, 4) for c in (1, 2, 3)]
    with pytest.raises(ValueError):
        ModuloControle(m=3).receber(lista)


def test_busca_completa_com_mensagem():
    produtos = gerar_produtos(500, seed=9)
    controle = ModuloControle()
    ModuloInspecao().processar(produtos, controle, exibir=False)
    consultas = gerar_consultas(produtos, 200, taxa_acerto=0.5, seed=9)
    resultados = controle.buscar(consultas)
    chaves = {p.chave_cliente for p in produtos}
    for r in resultados:
        if r.consulta.chave_cliente in chaves:
            assert r.encontrado
            assert r.registro.tamanho == r.consulta.tamanho
        else:
            assert r.mensagem == MENSAGEM_NAO_ENCONTRADO


def test_busca_sem_dados():
    [r] = ModuloControle().buscar([Consulta(1, 10)])
    assert r.mensagem == MENSAGEM_NAO_ENCONTRADO
