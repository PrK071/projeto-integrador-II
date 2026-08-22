# -*- coding: utf-8 -*-
"""
Camada de tratamento + calculo de indicadores.
Le os 3 anos do cadastro de cursos, padroniza, deriva indicadores e grava
tabelas tidy em outputs/tabelas/.

Execucao:  python -m src.indicators   (a partir da raiz do projeto)
"""
import numpy as np
import pandas as pd
from . import config as C


# ----------------------------------------------------------------------
# 1. Carga e padronizacao
# ----------------------------------------------------------------------
def carregar_ano(ano: int) -> pd.DataFrame:
    df = pd.read_csv(C.caminho_cursos(ano), usecols=C.USECOLS, **C.CSV_KW)
    df["ANO"] = ano
    # numericos
    num = C.COLS_FLUXO + C.COLS_SIT + C.COLS_DEMO
    for c in num:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    # rotulos
    df["MODALIDADE"] = df["TP_MODALIDADE_ENSINO"].map(C.MAP_MODALIDADE)
    df["GRAU"] = df["TP_GRAU_ACADEMICO"].map(C.MAP_GRAU).fillna("Nao aplicavel")
    df["REDE"] = df["TP_REDE"].map(C.MAP_REDE)
    df["CATEGORIA"] = df["TP_CATEGORIA_ADMINISTRATIVA"].map(C.MAP_CAT)
    df["EH_TI"] = C.eh_ti(df)
    # universo de vinculos (para proxies de evasao)
    df["BASE_VINCULOS"] = (df["QT_MAT"] + df["QT_SIT_TRANCADA"]
                           + df["QT_SIT_DESVINCULADO"] + df["QT_SIT_TRANSFERIDO"]
                           + df["QT_SIT_FALECIDO"])
    return df


def carregar_tudo() -> pd.DataFrame:
    return pd.concat([carregar_ano(a) for a in C.ANOS], ignore_index=True)


# ----------------------------------------------------------------------
# 2. Helpers de agregacao / indicadores
# ----------------------------------------------------------------------
SOMAS = (C.COLS_FLUXO + C.COLS_SIT + ["BASE_VINCULOS"])


def agrega(df, chaves):
    g = df.groupby(chaves, dropna=False).agg(
        {**{c: "sum" for c in SOMAS},
         "CO_IES": "nunique", "NO_CURSO": "count"}).reset_index()
    g = g.rename(columns={"CO_IES": "QT_IES", "NO_CURSO": "QT_CURSOS"})
    return _indicadores(g)


def _indicadores(g):
    base = g["BASE_VINCULOS"].replace(0, np.nan)
    g["TX_EVASAO_DESVINC_PCT"] = (g["QT_SIT_DESVINCULADO"] / base * 100).round(2)
    g["TX_TRANCAMENTO_PCT"] = (g["QT_SIT_TRANCADA"] / base * 100).round(2)
    g["TX_EVASAO_AMPLA_PCT"] = ((g["QT_SIT_DESVINCULADO"] + g["QT_SIT_TRANCADA"]
                                 + g["QT_SIT_TRANSFERIDO"]) / base * 100).round(2)
    g["TX_PERMANENCIA_PCT"] = (g["QT_MAT"] / base * 100).round(2)
    ing = g["QT_ING"].replace(0, np.nan)
    vg = g["QT_VG_TOTAL"].replace(0, np.nan)
    g["REL_CONC_ING_PCT"] = (g["QT_CONC"] / ing * 100).round(2)
    g["REL_CAND_VAGA"] = (g["QT_INSCRITO_TOTAL"] / vg).round(2)
    return g


def add_crescimento(g, chave_grupo, valor):
    """Adiciona crescimento % ano a ano e indice base 2022=100 por grupo."""
    g = g.sort_values(chave_grupo + ["ANO"]) if chave_grupo else g.sort_values("ANO")
    grp = g.groupby(chave_grupo) if chave_grupo else g.groupby(lambda _: 0)
    g[valor + "_CRESC_PCT"] = (grp[valor].pct_change() * 100).round(2)
    g[valor + "_IDX100"] = (grp[valor].transform(lambda s: s / s.iloc[0] * 100)).round(1)
    return g


def salvar(df, nome):
    p = C.TAB / f"{nome}.csv"
    df.to_csv(p, index=False, encoding="utf-8-sig")
    print(f"  gravado {nome}.csv  ({len(df)} linhas)")


# ----------------------------------------------------------------------
# 3. Producao das tabelas
# ----------------------------------------------------------------------
def main():
    print("Carregando microdados 2022-2024 ...")
    df = carregar_tudo()
    print(f"  {len(df):,} cursos-ano carregados")

    # ---- Dimensao 1: Evasao e retencao ----
    print("D1 evasao/retencao")
    salvar(add_crescimento(agrega(df, ["ANO"]), [], "QT_MAT"), "d1_evasao_nacional")
    salvar(agrega(df, ["ANO", "MODALIDADE"]), "d1_evasao_modalidade")
    salvar(agrega(df, ["ANO", "NO_REGIAO"]), "d1_evasao_regiao")
    salvar(agrega(df, ["ANO", "NO_CINE_AREA_GERAL"]), "d1_evasao_area")

    # ---- Dimensao 2: EAD vs Presencial ----
    print("D2 EAD vs presencial")
    m = agrega(df, ["ANO", "MODALIDADE"])
    m = add_crescimento(m, ["MODALIDADE"], "QT_MAT")
    m = add_crescimento(m, ["MODALIDADE"], "QT_ING")
    m = add_crescimento(m, ["MODALIDADE"], "QT_VG_TOTAL")
    m = add_crescimento(m, ["MODALIDADE"], "QT_CONC")
    # participacao % no total do ano
    for col in ["QT_MAT", "QT_ING", "QT_VG_TOTAL", "QT_CONC", "QT_IES"]:
        tot = m.groupby("ANO")[col].transform("sum")
        m[col + "_PART_PCT"] = (m[col] / tot * 100).round(2)
    salvar(m, "d2_modalidade_nacional")
    salvar(agrega(df, ["ANO", "NO_REGIAO", "MODALIDADE"]), "d2_modalidade_regiao")
    salvar(agrega(df, ["ANO", "SG_UF", "MODALIDADE"]), "d2_modalidade_uf")

    # ---- Dimensao 3: Demanda e distribuicao regional ----
    print("D3 demanda regional")
    salvar(add_crescimento(agrega(df, ["ANO", "NO_REGIAO"]), ["NO_REGIAO"], "QT_INSCRITO_TOTAL"),
           "d3_demanda_regiao")
    salvar(agrega(df, ["ANO", "SG_UF"]), "d3_demanda_uf")
    salvar(add_crescimento(agrega(df, ["ANO", "NO_CINE_AREA_GERAL"]),
                           ["NO_CINE_AREA_GERAL"], "QT_ING"), "d3_demanda_area")

    # ---- Dimensao 4: recorte TI ----
    print("D4 cursos de TI")
    ti = df[df["EH_TI"]].copy()
    # TI nacional + comparacao com total
    ti_nac = add_crescimento(agrega(ti, ["ANO"]), [], "QT_MAT")
    ti_nac = add_crescimento(ti_nac, [], "QT_ING")
    ti_nac = add_crescimento(ti_nac, [], "QT_CONC")
    tot_nac = agrega(df, ["ANO"])[["ANO", "QT_MAT", "QT_ING", "QT_CONC"]].rename(
        columns={"QT_MAT": "QT_MAT_TOTAL", "QT_ING": "QT_ING_TOTAL", "QT_CONC": "QT_CONC_TOTAL"})
    ti_nac = ti_nac.merge(tot_nac, on="ANO")
    ti_nac["PART_MAT_TI_PCT"] = (ti_nac["QT_MAT"] / ti_nac["QT_MAT_TOTAL"] * 100).round(2)
    ti_nac["PART_ING_TI_PCT"] = (ti_nac["QT_ING"] / ti_nac["QT_ING_TOTAL"] * 100).round(2)
    salvar(ti_nac, "d4_ti_nacional")
    salvar(add_crescimento(agrega(ti, ["ANO", "MODALIDADE"]), ["MODALIDADE"], "QT_MAT"),
           "d4_ti_modalidade")
    salvar(add_crescimento(agrega(ti, ["ANO", "NO_REGIAO"]), ["NO_REGIAO"], "QT_MAT"),
           "d4_ti_regiao")
    salvar(agrega(ti, ["ANO", "SG_UF"]), "d4_ti_uf")
    salvar(add_crescimento(agrega(ti, ["ANO", "NO_CINE_ROTULO"]), ["NO_CINE_ROTULO"], "QT_MAT"),
           "d4_ti_curso")
    salvar(agrega(ti, ["ANO", "GRAU"]), "d4_ti_grau")
    salvar(agrega(ti, ["ANO", "REDE"]), "d4_ti_rede")

    # perfil demografico TI (sexo + faixa etaria) sobre matriculas
    demo = ti.groupby("ANO").agg({**{c: "sum" for c in C.COLS_DEMO}, "QT_MAT": "sum"}).reset_index()
    demo["PCT_FEM"] = (demo["QT_MAT_FEM"] / demo["QT_MAT"] * 100).round(2)
    demo["PCT_MASC"] = (demo["QT_MAT_MASC"] / demo["QT_MAT"] * 100).round(2)
    salvar(demo, "d4_ti_perfil_sexo")
    # idade em formato longo
    linhas = []
    for _, r in demo.iterrows():
        for col, faixa in C.FAIXAS_ETARIAS.items():
            linhas.append({"ANO": int(r["ANO"]), "FAIXA": faixa,
                           "QT_MAT": r[col],
                           "PCT": round(r[col] / r["QT_MAT"] * 100, 2)})
    salvar(pd.DataFrame(linhas), "d4_ti_perfil_idade")

    print("OK - tabelas em outputs/tabelas/")


if __name__ == "__main__":
    main()
