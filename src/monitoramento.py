"""
Módulo de monitoramento (Tarefas 4 e 6).

Registra o histórico de desempenho dos módulos de inspeção e controle e gera os três gráficos exigidos:

1. Inspeção de produtos tipo 1;
2. Inspeção de produtos tipo 2;
3. Módulo de controle (inserção e busca).

Cada medição guarda o cenário da simulação ("quantidade" escalona o número de produtos na lista; "tamanho" escalona o tamanho dos produtos) e o valor do parâmetro escalonado naquela rodada.

"""
from __future__ import annotations

import csv
import statistics
from collections import defaultdict
from dataclasses import asdict, dataclass, fields
from pathlib import Path


@dataclass(frozen=True)
class Medicao:
    modulo: str
    cenario: str
    parametro: int
    quantidade: int
    tamanho_medio: float
    tempo_s: float
    metrica: float  # horas médias (inspeção), fator de carga (inserção), comparações médias (busca)


@dataclass(frozen=True)
class PontoAgregado:
    parametro: int
    tempo_ms: float
    desvio_ms: float
    metrica: float


class Monitor:
    def __init__(self) -> None:
        self.historico: list[Medicao] = []
        self._cenario = "manual"
        self._parametro = 0

    def definir_contexto(self, cenario: str, parametro: int) -> None:
        """Define o cenário e o parâmetro das próximas medições."""
        self._cenario = cenario
        self._parametro = parametro

    def registrar(
        self,
        modulo: str,
        quantidade: int,
        tamanho_medio: float,
        tempo_s: float,
        metrica: float = 0.0,
    ) -> Medicao:
        medicao = Medicao(modulo, self._cenario, self._parametro, quantidade, tamanho_medio, tempo_s, metrica)
        self.historico.append(medicao)
        return medicao

    def filtrar(self, modulo: str, cenario: str | None = None) -> list[Medicao]:
        return [m for m in self.historico if m.modulo == modulo and (cenario is None or m.cenario == cenario)]

    def agregar(self, modulo: str, cenario: str) -> list[PontoAgregado]:
        """Média (e desvio) das repetições para cada valor do parâmetro."""
        grupos: dict[int, list[Medicao]] = defaultdict(list)
        for m in self.filtrar(modulo, cenario):
            grupos[m.parametro].append(m)

        pontos = []
        for parametro in sorted(grupos):
            medicoes = grupos[parametro]
            tempos = [m.tempo_s * 1000 for m in medicoes]
            pontos.append(
                PontoAgregado(
                    parametro=parametro,
                    tempo_ms=statistics.mean(tempos),
                    desvio_ms=statistics.stdev(tempos) if len(tempos) > 1 else 0.0,
                    metrica=statistics.mean(m.metrica for m in medicoes),
                )
            )
        return pontos

    def salvar_csv(self, caminho: str | Path) -> Path:
        caminho = Path(caminho)
        caminho.parent.mkdir(parents=True, exist_ok=True)
        with caminho.open("w", newline="", encoding="utf-8") as arquivo:
            escritor = csv.DictWriter(arquivo, fieldnames=[f.name for f in fields(Medicao)])
            escritor.writeheader()
            for m in self.historico:
                escritor.writerow(asdict(m))
        return caminho

    # ------------------------------------------------------------------ gráficos

    @staticmethod
    def _sem_dados(ax, titulo: str) -> None:
        ax.set_title(titulo)
        ax.text(0.5, 0.5, "sem dados", ha="center", va="center", transform=ax.transAxes)

    @staticmethod
    def _finalizar(fig, caminho: str | Path | None, mostrar: bool):
        import matplotlib.pyplot as plt

        fig.tight_layout()
        if caminho is not None:
            Path(caminho).parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(caminho, dpi=130)
        if mostrar:
            plt.show()
        plt.close(fig)

    def plotar_inspecao(self, tipo: int, caminho: str | Path | None = None, mostrar: bool = False) -> None:
        """Gráfico do histórico de desempenho da inspeção de um tipo de produto."""
        import matplotlib.pyplot as plt

        modulo = f"inspecao_tipo{tipo}"
        complexidade = "O(log n)" if tipo == 1 else "O(n) passos, n(n+1)/2 horas"
        fig, (ax_qtd, ax_tam) = plt.subplots(1, 2, figsize=(13, 4.8))
        fig.suptitle(f"Módulo de inspeção — produto tipo {tipo}  [{complexidade}]", fontweight="bold")

        pontos = self.agregar(modulo, "quantidade")
        titulo = "Escalonando a quantidade de produtos"
        if pontos:
            x = [p.parametro for p in pontos]
            ax_qtd.errorbar(x, [p.tempo_ms for p in pontos], yerr=[p.desvio_ms for p in pontos],
                            marker="o", capsize=3, color="tab:blue")
            ax_qtd.set_title(titulo)
            ax_qtd.set_xlabel("Produtos na lista (tamanhos aleatórios)")
            ax_qtd.set_ylabel("Tempo de execução (ms)")
            ax_qtd.grid(alpha=0.3)
        else:
            self._sem_dados(ax_qtd, titulo)

        pontos = self.agregar(modulo, "tamanho")
        titulo = "Escalonando o tamanho dos produtos"
        if pontos:
            x = [p.parametro for p in pontos]
            linha_tempo = ax_tam.errorbar(x, [p.tempo_ms for p in pontos], yerr=[p.desvio_ms for p in pontos],
                                          marker="o", capsize=3, color="tab:blue", label="Tempo de execução")
            ax_tam.set_title(titulo)
            ax_tam.set_xlabel("Tamanho n do produto")
            ax_tam.set_ylabel("Tempo de execução (ms)")
            ax_tam.grid(alpha=0.3)
            ax_horas = ax_tam.twinx()
            (linha_horas,) = ax_horas.plot(x, [p.metrica for p in pontos], "s--", color="tab:orange",
                                           label="Horas de inspeção por produto")
            ax_horas.set_ylabel("Horas de inspeção por produto")
            ax_tam.legend(handles=[linha_tempo, linha_horas], loc="upper left")
        else:
            self._sem_dados(ax_tam, titulo)

        self._finalizar(fig, caminho, mostrar)

    def plotar_controle(self, caminho: str | Path | None = None, mostrar: bool = False) -> None:
        """Gráfico do histórico de desempenho do módulo de controle."""
        import matplotlib.pyplot as plt

        fig, (ax_tempo, ax_comp) = plt.subplots(1, 2, figsize=(13, 4.8))
        fig.suptitle("Módulo de controle — tabela hash com encadeamento  [O(1 + α) por operação]",
                     fontweight="bold")

        insercao = self.agregar("controle_insercao", "quantidade")
        busca = self.agregar("controle_busca", "quantidade")
        titulo = "Tempo total por lista"
        if insercao or busca:
            for pontos, rotulo, cor in ((insercao, "Inserção", "tab:green"), (busca, "Busca", "tab:purple")):
                if pontos:
                    ax_tempo.errorbar([p.parametro for p in pontos], [p.tempo_ms for p in pontos],
                                      yerr=[p.desvio_ms for p in pontos], marker="o", capsize=3,
                                      color=cor, label=rotulo)
            ax_tempo.set_title(titulo)
            ax_tempo.set_xlabel("Produtos na lista / buscas realizadas")
            ax_tempo.set_ylabel("Tempo de execução (ms)")
            ax_tempo.legend()
            ax_tempo.grid(alpha=0.3)
        else:
            self._sem_dados(ax_tempo, titulo)

        titulo = "Custo médio por operação"
        if insercao or busca:
            if busca:
                ax_comp.plot([p.parametro for p in busca], [p.metrica for p in busca], "o-",
                             color="tab:purple", label="Comparações por busca")
            if insercao:
                ax_comp.plot([p.parametro for p in insercao], [p.metrica for p in insercao], "s--",
                             color="tab:green", label="Fator de carga α = n/m")
            ax_comp.set_title(titulo)
            ax_comp.set_xlabel("Produtos na lista")
            ax_comp.set_ylim(bottom=0)
            ax_comp.legend()
            ax_comp.grid(alpha=0.3)
        else:
            self._sem_dados(ax_comp, titulo)

        self._finalizar(fig, caminho, mostrar)

    def gerar_graficos(self, pasta: str | Path, mostrar: bool = False) -> list[Path]:
        pasta = Path(pasta)
        caminhos = [pasta / "inspecao_tipo1.png", pasta / "inspecao_tipo2.png", pasta / "controle.png"]
        self.plotar_inspecao(1, caminhos[0], mostrar)
        self.plotar_inspecao(2, caminhos[1], mostrar)
        self.plotar_controle(caminhos[2], mostrar)
        return caminhos