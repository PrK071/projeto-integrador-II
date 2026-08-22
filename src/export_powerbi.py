# -*- coding: utf-8 -*-
"""
Exporta uma tabela-fato tratada, pronta para Power BI / Tableau / etc.

Grao: um registro por curso-ano (mesmo grao do cadastro de cursos do INEP).
Saidas em data/processed/:
    fato_cursos.parquet   (compacto, recomendado para Power BI Desktop)
    fato_cursos.csv       (universal, fallback)
    dim_ano.csv           (dimensao calendario simples)

As TAXAS (evasao, permanencia, participacao, crescimento) NAO sao gravadas
como coluna: devem virar MEDIDAS DAX no Power BI, para respeitar o filtro do
usuario (ver docs/POWERBI.md).

Execucao:  python -m src.export_powerbi
"""
import pandas as pd
from . import config as C
from .indicators import carregar_tudo

# colunas finais da tabela-fato (dimensoes + medidas base somaveis)
DIMS = ["ANO", "NO_REGIAO", "SG_UF", "NO_UF", "CO_IES",
        "CATEGORIA", "REDE", "NO_CURSO", "NO_CINE_AREA_GERAL",
        "NO_CINE_ROTULO", "GRAU", "MODALIDADE", "EH_TI"]
MEDIDAS = (C.COLS_FLUXO + C.COLS_SIT + ["BASE_VINCULOS"]
           + ["QT_MAT_FEM", "QT_MAT_MASC"])


def main():
    print("Carregando e tratando ...")
    df = carregar_tudo()
    df["EH_TI"] = df["EH_TI"].map({True: "TI", False: "Outros"})
    fato = df[DIMS + MEDIDAS].copy()

    p_parq = C.PROC / "fato_cursos.parquet"
    p_csv = C.PROC / "fato_cursos.csv"
    fato.to_parquet(p_parq, index=False)
    fato.to_csv(p_csv, index=False, encoding="utf-8-sig")

    # dimensao calendario minima
    pd.DataFrame({"ANO": C.ANOS}).to_csv(C.PROC / "dim_ano.csv", index=False)

    mb = p_parq.stat().st_size / 1e6
    csv_mb = p_csv.stat().st_size / 1e6
    print(f"  fato_cursos.parquet  {len(fato):,} linhas  {mb:.1f} MB")
    print(f"  fato_cursos.csv      {csv_mb:.1f} MB")
    print("OK - importe o .parquet no Power BI (Obter Dados > Parquet).")


if __name__ == "__main__":
    main()
