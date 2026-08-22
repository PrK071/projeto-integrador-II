# -*- coding: utf-8 -*-
"""
Gera as visualizacoes (outputs/figuras/) a partir das tabelas tidy.
Cada figura responde a uma pergunta de pesquisa.

Execucao:  python -m src.figures
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from . import config as C

plt.rcParams.update({"figure.dpi": 120, "font.size": 10,
                     "axes.grid": True, "grid.alpha": .3})
T = C.TAB


def _tab(n):
    return pd.read_csv(T / f"{n}.csv")


def _save(fig, nome):
    fig.tight_layout()
    fig.savefig(C.FIG / f"{nome}.png", bbox_inches="tight")
    plt.close(fig)
    print(f"  figura {nome}.png")


# ---------------- Dimensao 1 ----------------
def d1():
    d = _tab("d1_evasao_nacional")
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(d.ANO, d.TX_EVASAO_DESVINC_PCT, "o-", label="Evasao (desvinculacao)")
    ax.plot(d.ANO, d.TX_EVASAO_AMPLA_PCT, "s-", label="Evasao ampla (desv+tranc+transf)")
    ax.plot(d.ANO, d.TX_PERMANENCIA_PCT, "^-", label="Permanencia")
    ax.set_xticks(d.ANO); ax.set_ylabel("% dos vinculos"); ax.set_ylim(0, 75)
    ax.set_title("D1 - Evasao e permanencia (proxy transversal) - Brasil")
    ax.legend()
    _save(fig, "d1_evasao_nacional")

    m = _tab("d1_evasao_modalidade")
    fig, ax = plt.subplots(figsize=(7, 4))
    for mod, sub in m.groupby("MODALIDADE"):
        ax.plot(sub.ANO, sub.TX_EVASAO_DESVINC_PCT, "o-", label=mod)
    ax.set_xticks(m.ANO.unique()); ax.set_ylabel("Taxa de desvinculacao %")
    ax.set_title("D1 - Evasao (desvinculacao): EAD vs Presencial")
    ax.legend()
    _save(fig, "d1_evasao_modalidade")


# ---------------- Dimensao 2 ----------------
def d2():
    m = _tab("d2_modalidade_nacional")
    piv = m.pivot(index="ANO", columns="MODALIDADE", values="QT_MAT")
    fig, ax = plt.subplots(figsize=(7, 4))
    piv.plot(marker="o", ax=ax)
    ax.set_ylabel("Matriculas"); ax.set_title("D2 - Matriculas: EAD vs Presencial")
    ax.set_xticks(piv.index)
    _save(fig, "d2_matriculas_modalidade")

    part = m.pivot(index="ANO", columns="MODALIDADE", values="QT_MAT_PART_PCT")
    fig, ax = plt.subplots(figsize=(7, 4))
    part.plot(kind="bar", stacked=True, ax=ax)
    ax.set_ylabel("Participacao % nas matriculas")
    ax.set_title("D2 - Participacao EAD vs Presencial no total")
    for c in ax.containers:
        ax.bar_label(c, fmt="%.1f", label_type="center")
    _save(fig, "d2_participacao_modalidade")

    fig, ax = plt.subplots(figsize=(7, 4))
    for col, lab in [("QT_ING", "Ingressantes"), ("QT_VG_TOTAL", "Vagas")]:
        p = m.pivot(index="ANO", columns="MODALIDADE", values=col)
        for mod in p.columns:
            ax.plot(p.index, p[mod], "o-", label=f"{lab} - {mod}")
    ax.set_ylabel("Quantidade"); ax.set_xticks(m.ANO.unique())
    ax.set_title("D2 - Vagas e ingressantes por modalidade")
    ax.legend(fontsize=8)
    _save(fig, "d2_vagas_ingressantes")


# ---------------- Dimensao 3 ----------------
def d3():
    r = _tab("d2_modalidade_regiao")
    r = r[r.NO_REGIAO.notna()]
    # demanda (matriculas) por regiao e ano
    piv = r.groupby(["ANO", "NO_REGIAO"]).QT_MAT.sum().unstack("NO_REGIAO")
    fig, ax = plt.subplots(figsize=(8, 4.5))
    piv.plot(kind="bar", ax=ax)
    ax.set_ylabel("Matriculas"); ax.set_title("D3 - Matriculas por regiao")
    ax.legend(fontsize=8, ncol=5)
    _save(fig, "d3_matriculas_regiao")

    # relacao candidato/vaga PRESENCIAL (vagas EAD nao sao regionalizadas)
    pres = r[r.MODALIDADE == "Presencial"].copy()
    pres["REL"] = pres.QT_INSCRITO_TOTAL / pres.QT_VG_TOTAL
    piv2 = pres.pivot(index="NO_REGIAO", columns="ANO", values="REL")
    fig, ax = plt.subplots(figsize=(8, 4.5))
    piv2.plot(kind="barh", ax=ax)
    ax.set_xlabel("Inscritos / vaga (presencial)")
    ax.set_title("D3 - Relacao candidato/vaga por regiao (presencial)")
    _save(fig, "d3_candidato_vaga_regiao")

    # ranking UF por matriculas 2024
    uf = _tab("d3_demanda_uf")
    uf = uf[(uf.ANO == 2024) & uf.SG_UF.notna()].sort_values("QT_MAT", ascending=True)
    fig, ax = plt.subplots(figsize=(7, 8))
    ax.barh(uf.SG_UF, uf.QT_MAT)
    ax.set_xlabel("Matriculas 2024"); ax.set_title("D3 - Ranking de UF por matriculas (2024)")
    _save(fig, "d3_ranking_uf")


# ---------------- Dimensao 4 ----------------
def d4():
    n = _tab("d4_ti_nacional")
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(n.ANO, n.QT_MAT, "o-", label="Matriculas")
    ax.plot(n.ANO, n.QT_ING, "s-", label="Ingressantes")
    ax.plot(n.ANO, n.QT_CONC, "^-", label="Concluintes")
    ax.set_xticks(n.ANO); ax.set_ylabel("Quantidade"); ax.legend()
    ax.set_title("D4 - TI: matriculas, ingressantes e concluintes")
    _save(fig, "d4_ti_fluxo")

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(n.ANO, n.PART_MAT_TI_PCT, "o-", label="% matriculas TI no total")
    ax.plot(n.ANO, n.PART_ING_TI_PCT, "s-", label="% ingressantes TI no total")
    ax.set_xticks(n.ANO); ax.set_ylabel("% do ensino superior")
    ax.set_title("D4 - Participacao dos cursos de TI no total")
    ax.legend()
    _save(fig, "d4_ti_participacao")

    # ranking de cursos de TI por matriculas 2024
    c = _tab("d4_ti_curso")
    c = c[c.ANO == 2024].sort_values("QT_MAT", ascending=False).head(10).sort_values("QT_MAT")
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(c.NO_CINE_ROTULO.str.slice(0, 40), c.QT_MAT)
    ax.set_xlabel("Matriculas 2024"); ax.set_title("D4 - Top 10 cursos de TI (matriculas 2024)")
    _save(fig, "d4_ti_top_cursos")

    # modalidade TI
    m = _tab("d4_ti_modalidade")
    piv = m.pivot(index="ANO", columns="MODALIDADE", values="QT_MAT")
    fig, ax = plt.subplots(figsize=(7, 4))
    piv.plot(kind="bar", stacked=True, ax=ax)
    ax.set_ylabel("Matriculas TI"); ax.set_title("D4 - TI: EAD vs Presencial")
    _save(fig, "d4_ti_modalidade")

    # regiao TI
    r = _tab("d4_ti_regiao")
    r = r[r.NO_REGIAO.notna()]
    piv = r.pivot(index="ANO", columns="NO_REGIAO", values="QT_MAT")
    fig, ax = plt.subplots(figsize=(8, 4.5))
    piv.plot(kind="bar", ax=ax)
    ax.set_ylabel("Matriculas TI"); ax.set_title("D4 - TI por regiao")
    ax.legend(fontsize=8, ncol=5)
    _save(fig, "d4_ti_regiao")

    # perfil idade TI
    idade = _tab("d4_ti_perfil_idade")
    piv = idade.pivot(index="FAIXA", columns="ANO", values="PCT")
    fig, ax = plt.subplots(figsize=(8, 4.5))
    piv.plot(kind="bar", ax=ax)
    ax.set_ylabel("% das matriculas TI"); ax.set_xlabel("Faixa etaria")
    ax.set_title("D4 - Perfil etario dos estudantes de TI")
    _save(fig, "d4_ti_perfil_idade")

    # perfil sexo TI
    s = _tab("d4_ti_perfil_sexo")
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(s.ANO - 0.2, s.PCT_FEM, width=0.4, label="Feminino")
    ax.bar(s.ANO + 0.2, s.PCT_MASC, width=0.4, label="Masculino")
    ax.set_xticks(s.ANO); ax.set_ylabel("% das matriculas TI")
    ax.set_title("D4 - Distribuicao por sexo (TI)"); ax.legend()
    _save(fig, "d4_ti_perfil_sexo")


def main():
    print("Gerando figuras ...")
    d1(); d2(); d3(); d4()
    print("OK - figuras em outputs/figuras/")


if __name__ == "__main__":
    main()
