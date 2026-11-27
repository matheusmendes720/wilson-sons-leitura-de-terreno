"""Caso trabalhado + geração do catálogo. python3 demo.py"""
from datetime import date

from regras import Operacao, avaliar, catalogo_markdown, resumo

CASOS = [
    ("Caso A — operação de rotina registada em DUIMP a 16/11/2026",
     Operacao(data_registro=date(2026, 11, 16), documento="DUIMP", tipo="importacao",
              ncm="84713012", chegada_carga=date(2026, 11, 20), recepcao_carga=date(2026, 11, 21),
              data_saida=date(2026, 12, 15))),
    ("Caso B — o mesmo, mas registado em DI a 11/12/2026 (dois dias após o desligamento)",
     Operacao(data_registro=date(2026, 12, 11), documento="DI", tipo="importacao",
              ncm="84713012", chegada_carga=date(2026, 12, 15), recepcao_carga=date(2026, 12, 16),
              data_saida=date(2026, 12, 20))),
    ("Caso C — NCM extinta em 2024 usada numa operação registada em 2026",
     Operacao(data_registro=date(2026, 11, 16), documento="DUIMP", tipo="importacao",
              ncm="85045000", chegada_carga=date(2026, 11, 20), recepcao_carga=date(2026, 11, 21),
              data_saida=date(2026, 12, 15))),
]


def main() -> None:
    print("=" * 96)
    print("MOTOR DE REGRAS — FLUXO DE IMPORTAÇÃO · DEMONSTRAÇÃO")
    print("=" * 96)
    for titulo, operacao in CASOS:
        print(f"\n{titulo}")
        print("-" * 96)
        decisoes = avaliar(operacao)
        for d in decisoes:
            print("  " + str(d))
        print(f"\n  >>> RESULTADO AGREGADO: {resumo(decisoes)}")
    with open("catalogo_regras.md", "w", encoding="utf-8") as fh:
        fh.write(catalogo_markdown())
    print("\n[catálogo gerado em catalogo_regras.md]")


if __name__ == "__main__":
    main()
