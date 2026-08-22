# Projeto Integrador — Panorama do Ensino Superior Brasileiro

Análise quantitativa dos **Microdados do Censo da Educação Superior (INEP)** — edições **2022, 2023 e 2024** — sobre quatro dimensões: **evasão/retenção**, **EAD vs. presencial**, **demanda regional** e **expansão dos cursos de TI**.

## Estrutura

```
projeto_censo_sup/
├── data/raw/            # zips do INEP + CSVs extraídos por ano
├── outputs/tabelas/     # tabelas de indicadores (CSV, tidy)
├── outputs/figuras/     # visualizações (PNG)
├── docs/RELATORIO.md    # relatório analítico (leitura principal)
└── src/
    ├── config.py        # caminhos, colunas, mapeamentos, filtro de TI
    ├── indicators.py    # ETL + cálculo de indicadores  -> tabelas
    └── figures.py       # gráficos -> figuras
```

## Reprodução

Pré-requisitos: Python 3.11+, `pandas`, `numpy`, `matplotlib`, `openpyxl`.

```bash
pip install pandas numpy matplotlib openpyxl

# 1) Baixar os microdados (uma vez), na pasta data/raw/:
#    https://download.inep.gov.br/microdados/microdados_censo_da_educacao_superior_2022.zip
#    (idem 2023 e 2024) e extrair CURSOS_<ano>.CSV para data/raw/<ano>/

# 2) Gerar indicadores e figuras (a partir da raiz do projeto):
python -m src.indicators
python -m src.figures
```

## Fonte dos dados

INEP — Censo da Educação Superior, arquivo **Cadastro de Cursos**
<https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-da-educacao-superior>

Licença: Creative Commons Atribuição-SemDerivações 3.0.

## Avisos metodológicos

- Usa o **Cadastro de Cursos** (contagens agregadas), não o módulo Aluno nominal.
- As **taxas de evasão são proxies transversais** (não coorte). Ver `docs/RELATORIO.md`, seção 1.
- **Vagas de EAD não são regionalizadas**; relação candidato/vaga é interpretada só no presencial.
- **TI** = área CINE 6 (Computação e TIC) + "Engenharia de computação" (classificação derivada).
