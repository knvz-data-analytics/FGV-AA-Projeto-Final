from monitoramento import Monitor
from simulacao import simular


def test_agregacao_media():
    monitor = Monitor()
    monitor.definir_contexto("quantidade", 10)
    monitor.registrar("controle_busca", 10, 50, 0.002, metrica=2)
    monitor.registrar("controle_busca", 10, 50, 0.004, metrica=4)
    [ponto] = monitor.agregar("controle_busca", "quantidade")
    assert ponto.parametro == 10
    assert abs(ponto.tempo_ms - 3.0) < 1e-9
    assert ponto.metrica == 3


def test_simulacao_gera_graficos_e_csv(tmp_path):
    monitor = Monitor()
    simular(monitor, quantidades=(10, 50), tamanhos=(10, 50), quantidade_fixa=20,
            repeticoes=2, log=lambda _: None)
    modulos = {m.modulo for m in monitor.historico}
    assert {"inspecao_tipo1", "inspecao_tipo2", "controle_insercao", "controle_busca"} <= modulos
    graficos = monitor.gerar_graficos(tmp_path)
    assert all(g.exists() and g.stat().st_size > 0 for g in graficos)
    assert monitor.salvar_csv(tmp_path / "m.csv").exists()


def test_graficos_sem_dados(tmp_path):
    assert all(g.exists() for g in Monitor().gerar_graficos(tmp_path))
