# -*- coding: utf-8 -*-
"""
Configuracao central do projeto.
Microdados do Censo da Educacao Superior (INEP) - arquivo CADASTRO DE CURSOS.
Anos: 2022, 2023, 2024.

IMPORTANTE (metodologia):
- QT_MAT = alunos com vinculo "Cursando e/ou Formado" (NAO inclui trancados,
  desvinculados, transferidos nem falecidos).
- QT_SIT_TRANCADA / DESVINCULADO / TRANSFERIDO / FALECIDO sao contagens de
  vinculo SEPARADAS de QT_MAT.
- Portanto o universo de vinculos do ano = QT_MAT + as 4 situacoes acima.
- O Censo (cadastro de cursos) e um retrato TRANSVERSAL anual. Nao permite
  acompanhar coortes. Toda "taxa de evasao" aqui e um PROXY transversal,
  nao uma taxa de evasao longitudinal de coorte.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed"
TAB = ROOT / "outputs" / "tabelas"
FIG = ROOT / "outputs" / "figuras"
for _p in (PROC, TAB, FIG):
    _p.mkdir(parents=True, exist_ok=True)

ANOS = [2022, 2023, 2024]
CSV_KW = dict(sep=";", encoding="latin-1", low_memory=False)

def caminho_cursos(ano: int) -> Path:
    return RAW / str(ano) / f"CURSOS_{ano}.CSV"

# ---- colunas lidas (usecols) para eficiencia ----
COLS_GEO = ["NU_ANO_CENSO", "NO_REGIAO", "CO_REGIAO", "NO_UF", "SG_UF", "CO_UF"]
COLS_INST = ["TP_CATEGORIA_ADMINISTRATIVA", "TP_REDE", "CO_IES"]
COLS_CURSO = ["NO_CURSO", "CO_CINE_ROTULO", "NO_CINE_ROTULO",
              "CO_CINE_AREA_GERAL", "NO_CINE_AREA_GERAL",
              "TP_GRAU_ACADEMICO", "TP_MODALIDADE_ENSINO", "TP_NIVEL_ACADEMICO"]
COLS_FLUXO = ["QT_VG_TOTAL", "QT_INSCRITO_TOTAL", "QT_ING", "QT_MAT", "QT_CONC"]
COLS_SIT = ["QT_SIT_TRANCADA", "QT_SIT_DESVINCULADO",
            "QT_SIT_TRANSFERIDO", "QT_SIT_FALECIDO"]
COLS_DEMO = ["QT_MAT_FEM", "QT_MAT_MASC",
             "QT_MAT_0_17", "QT_MAT_18_24", "QT_MAT_25_29", "QT_MAT_30_34",
             "QT_MAT_35_39", "QT_MAT_40_49", "QT_MAT_50_59", "QT_MAT_60_MAIS"]

USECOLS = COLS_GEO + COLS_INST + COLS_CURSO + COLS_FLUXO + COLS_SIT + COLS_DEMO

# ---- mapeamentos (dicionario de dados INEP) ----
MAP_MODALIDADE = {1: "Presencial", 2: "EAD"}
MAP_GRAU = {1: "Bacharelado", 2: "Licenciatura", 3: "Tecnologico",
            4: "Bacharelado e Licenciatura"}
MAP_REDE = {1: "Publica", 2: "Privada"}
MAP_CAT = {1: "Publica Federal", 2: "Publica Estadual", 3: "Publica Municipal",
           4: "Privada c/ fins lucrativos", 5: "Privada s/ fins lucrativos",
           6: "Privada particular", 7: "Especial",
           8: "Privada comunitaria", 9: "Privada confessional"}

FAIXAS_ETARIAS = {
    "QT_MAT_0_17": "0-17", "QT_MAT_18_24": "18-24", "QT_MAT_25_29": "25-29",
    "QT_MAT_30_34": "30-34", "QT_MAT_35_39": "35-39", "QT_MAT_40_49": "40-49",
    "QT_MAT_50_59": "50-59", "QT_MAT_60_MAIS": "60+"}

# ---- recorte de cursos de TI (classificacao derivada) ----
# Regra: area geral CINE 6 (Computacao e TIC) + rotulo "Engenharia de computacao"
# (que fica na area geral 7 - Engenharia). Documentado como indicador DERIVADO.
def eh_ti(df):
    area_tic = df["CO_CINE_AREA_GERAL"] == 6
    eng_comp = df["NO_CINE_ROTULO"].str.contains("Engenharia de computa",
                                                 case=False, na=False)
    return area_tic | eng_comp
