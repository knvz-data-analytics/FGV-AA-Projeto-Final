import pytest

from gerador import carregar_produtos_csv, gerar_consultas, gerar_produtos, salvar_produtos_csv


def test_gera_quantidade_e_faixas():
    produtos = gerar_produtos(1000, 10, 10_000, seed=1)
    assert len(produtos) == 1000
    assert all(10 <= p.tamanho <= 10_000 for p in produtos)
    assert {p.tipo for p in produtos} == {1, 2}


def test_seed_reprodutivel():
    assert gerar_produtos(50, seed=7) == gerar_produtos(50, seed=7)


@pytest.mark.parametrize("args", [(0,), (10, 50, 20), (10, 0, 5)])
def test_parametros_invalidos(args):
    with pytest.raises(ValueError):
        gerar_produtos(*args)


def test_csv_ida_e_volta(tmp_path):
    produtos = gerar_produtos(30, seed=3)
    caminho = salvar_produtos_csv(produtos, tmp_path / "lista.csv")
    assert carregar_produtos_csv(caminho) == produtos


def test_csv_rejeita_tipo_invalido(tmp_path):
    caminho = tmp_path / "ruim.csv"
    caminho.write_text("chave_cliente,tipo,tamanho\n1,3,10\n", encoding="utf-8")
    with pytest.raises(ValueError, match="linha 2"):
        carregar_produtos_csv(caminho)


def test_consultas_sem_acerto_usam_chaves_inexistentes():
    produtos = gerar_produtos(100, seed=2)
    chaves = {p.chave_cliente for p in produtos}
    consultas = gerar_consultas(produtos, 50, taxa_acerto=0.0, seed=2)
    assert all(c.chave_cliente not in chaves for c in consultas)
