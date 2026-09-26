"""

Interface de exibição das listas do sistema no terminal (Tarefa 2)

"""

from __future__ import annotations

from typing import Sequence

from gerador import Produto

def formatar_tabela(
    cabecalho: Sequence[str],
    linhas: Sequence[Sequence[object]],
    limite: int | None = 20,
) -> str:
    """Formata linhas como tabela de texto.

    Se houver mais linhas que ``limite``, mostra o início e o fim da lista
    e indica quantas linhas foram omitidas. ``limite=None`` mostra tudo.
    """
    linhas = [[str(celula) for celula in linha] for linha in linhas]
    omitidas = 0
    if limite is not None and len(linhas) > limite:
        metade = max(1, limite // 2)
        omitidas = len(linhas) - 2 * metade
        linhas = linhas[:metade] + [None] + linhas[-metade:]

    visiveis = [linha for linha in linhas if linha is not None]
    larguras = [
        max([len(cabecalho[i])] + [len(linha[i]) for linha in visiveis])
        for i in range(len(cabecalho))
    ]

    def montar(celulas: Sequence[str]) -> str:
        return " | ".join(c.rjust(larguras[i]) for i, c in enumerate(celulas))

    separador = "-+-".join("-" * l for l in larguras)
    saida = [montar(cabecalho), separador]
    for linha in linhas:
        if linha is None:
            saida.append(f"... ({omitidas} linhas omitidas) ...".center(len(separador)))
        else:
            saida.append(montar(linha))
    return "\n".join(saida)


def resumo_produtos(produtos: Sequence[Produto]) -> str:
    """Resumo de uma linha de uma lista de produtos."""
    tipo1 = sum(1 for p in produtos if p.tipo == 1)
    tamanhos = [p.tamanho for p in produtos]
    clientes = len({p.chave_cliente for p in produtos})
    return (
        f"{len(produtos)} produtos | tipo 1: {tipo1} | tipo 2: {len(produtos) - tipo1} | "
        f"tamanhos {min(tamanhos)}–{max(tamanhos)} | {clientes} clientes distintos"
    )


def exibir_produtos(produtos: Sequence[Produto], titulo: str, limite: int | None = 20) -> None:
    """Exibe a lista de dados fornecida ao sistema."""
    print(f"\n=== {titulo} ===")
    print(resumo_produtos(produtos))
    linhas = [(i, p.chave_cliente, p.tipo, p.tamanho) for i, p in enumerate(produtos, start=1)]
    print(formatar_tabela(("#", "Chave cliente", "Tipo", "Tamanho"), linhas, limite))


def formatar_horas(horas: int) -> str:
    """Formata horas com separador de milhar no padrão brasileiro (1.234.567)."""
    return f"{horas:,}".replace(",", ".")