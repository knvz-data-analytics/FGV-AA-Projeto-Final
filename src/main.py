"""

Sistema de Controle de Estoque Industrial

Uso:
    python src/main.py demo [--quantidade 15] [--entrada arquivo.csv] ...
    python src/main.py simular [--rapido] [--repeticoes 3] [--saida resultados] ...
    python src/main.py gerar --quantidade 1000 --saida entradas/lista.csv

"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import matplotlib

from gerador import carregar_produtos_csv, gerar_consultas, gerar_produtos, salvar_produtos_csv
from interface import exibir_produtos


def cmd_demo(args: argparse.Namespace) -> None:
    from controle import ModuloControle
    from inspecao import ModuloInspecao

    if args.entrada:
        produtos = carregar_produtos_csv(args.entrada)
        origem = f"Lista de entrada ({args.entrada})"
    else:
        produtos = gerar_produtos(args.quantidade, args.tamanho_min, args.tamanho_max, seed=args.seed)
        origem = "Lista de entrada (gerada)"
    limite = None if args.completo else args.limite

    exibir_produtos(produtos, origem, limite)

    controle = ModuloControle(m=args.m)
    ModuloInspecao().processar(produtos, controle, exibir=True, limite=limite)

    est = controle.tabela.estatisticas()
    k = len({p.chave_cliente for p in produtos})
    print(
        f"\n=== Estoque ===\nk = {k} chaves de cliente | m = {est['m']} tipos de cliente | "
        f"{est['n']} registros | fator de carga α = {est['fator_carga']:.2f} | "
        f"maior tipo = {est['maior_balde']} registros"
    )

    consultas = gerar_consultas(produtos, args.consultas, taxa_acerto=0.7, seed=args.seed)
    controle.exibir_resultados(controle.buscar(consultas), limite)


def cmd_simular(args: argparse.Namespace) -> None:
    from monitoramento import Monitor
    from simulacao import QUANTIDADES, QUANTIDADES_RAPIDO, TAMANHOS, TAMANHOS_RAPIDO, simular

    monitor = Monitor()
    inicio = time.perf_counter()
    simular(
        monitor,
        quantidades=QUANTIDADES_RAPIDO if args.rapido else QUANTIDADES,
        tamanhos=TAMANHOS_RAPIDO if args.rapido else TAMANHOS,
        repeticoes=args.repeticoes,
        seed=args.seed,
        exibir_entradas=args.exibir_entradas,
    )
    print(f"\nSimulação concluída em {time.perf_counter() - inicio:.1f} s")

    saida = Path(args.saida)
    csv_path = monitor.salvar_csv(saida / "medicoes.csv")
    graficos = monitor.gerar_graficos(saida, mostrar=args.mostrar)
    print(f"Medições: {csv_path}")
    for g in graficos:
        print(f"Gráfico:  {g}")


def cmd_gerar(args: argparse.Namespace) -> None:
    produtos = gerar_produtos(args.quantidade, args.tamanho_min, args.tamanho_max, seed=args.seed)
    caminho = salvar_produtos_csv(produtos, args.saida)
    print(f"{len(produtos)} produtos salvos em {caminho}")


def criar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Sistema de Controle de Estoque Industrial")
    sub = parser.add_subparsers(dest="comando", required=True)

    def faixa(p: argparse.ArgumentParser) -> None:
        p.add_argument("--tamanho-min", type=int, default=10)
        p.add_argument("--tamanho-max", type=int, default=10_000)
        p.add_argument("--seed", type=int, default=None, help="semente para reprodutibilidade")

    demo = sub.add_parser("demo", help="executa o sistema uma vez, exibindo todas as listas")
    demo.add_argument("--quantidade", type=int, default=15)
    demo.add_argument("--entrada", help="CSV com colunas chave_cliente,tipo,tamanho")
    demo.add_argument("--consultas", type=int, default=10, help="quantidade de buscas")
    demo.add_argument("--m", type=int, default=None, help="tipos de cliente (padrão: automático)")
    demo.add_argument("--limite", type=int, default=20, help="linhas exibidas por tabela")
    demo.add_argument("--completo", action="store_true", help="exibe as listas inteiras")
    faixa(demo)
    demo.set_defaults(func=cmd_demo)

    sim = sub.add_parser("simular", help="simulação completa com gráficos de desempenho")
    sim.add_argument("--repeticoes", type=int, default=3)
    sim.add_argument("--rapido", action="store_true", help="faixas menores, para testes rápidos")
    sim.add_argument("--saida", default="resultados")
    sim.add_argument("--seed", type=int, default=42)
    sim.add_argument("--mostrar", action="store_true", help="abre os gráficos em janelas")
    sim.add_argument("--exibir-entradas", action="store_true", help="exibe a lista de entrada de cada rodada")
    sim.set_defaults(func=cmd_simular)

    gerar = sub.add_parser("gerar", help="gera uma lista de produtos em CSV")
    gerar.add_argument("--quantidade", type=int, required=True)
    gerar.add_argument("--saida", required=True)
    faixa(gerar)
    gerar.set_defaults(func=cmd_gerar)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = criar_parser().parse_args(argv)
    if not getattr(args, "mostrar", False):
        matplotlib.use("Agg")  # salva os gráficos sem abrir janelas
    try:
        args.func(args)
    except (ValueError, FileNotFoundError) as erro:
        print(f"Erro: {erro}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())