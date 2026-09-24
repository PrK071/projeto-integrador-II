# Projeto Integrador — Panorama do Ensino Superior Brasileiro

Análise quantitativa dos **Microdados do Censo da Educação Superior (INEP)** — edições **2022, 2023 e 2024** — sobre quatro dimensões: **evasão/retenção**, **EAD vs. presencial**, **demanda regional** e **expansão dos cursos de TI**.

## Sobre o projeto

Este Projeto Integrador transforma os dados públicos do Cadastro de Cursos do INEP em uma análise reproduzível do ensino superior brasileiro. A proposta é organizar quase 2 milhões de registros curso-ano, calcular indicadores comparáveis entre 2022 e 2024 e apresentar os resultados em tabelas, gráficos, relatório analítico e uma base pronta para uso no Power BI.

O trabalho busca responder quatro perguntas principais:

1. Como evoluíram os indicadores de evasão, retenção e permanência?
2. Quais diferenças aparecem entre os cursos EAD e presenciais?
3. Como matrículas, procura e oferta se distribuem entre regiões e estados?
4. Como os cursos de Computação e Tecnologia da Informação cresceram no período?

O projeto não acompanha alunos individualmente e não utiliza dados pessoais. A unidade analisada é o curso em cada ano, com contagens agregadas publicadas pelo INEP. Por isso, as taxas de evasão apresentadas são aproximações transversais e não permitem atribuir causas ou acompanhar uma mesma turma ao longo do tempo.

## Dashboard web

O dashboard foi criado e validado no navegador, com:

- KPIs de matrículas, concluintes, participação de TI e evasão.
- Gráficos de evolução, modalidade, regiões e principais cursos.
- Filtro interativo por ano.
- Perfil por gênero e idade.
- Download dos indicadores em CSV.
- Relação com o mercado de trabalho, incluindo o cenário da [Brasscom](https://brasscom.org.br/macrossetor-de-tic-pode-gerar-ate-147-mil-empregos-formais-no-brasil-em-2025-aponta-estudo/).
- Alertas metodológicos para não confundir formação com empregabilidade ou vagas reais.

Para visualizar, abra [`dashboard/index.html`](dashboard/index.html) no navegador ou execute, na raiz do projeto:

```bash
python -m http.server 8000
```

Depois acesse <http://localhost:8000/dashboard/>.

## Como o projeto funciona

O fluxo parte dos arquivos anuais do INEP e segue quatro etapas:

1. `src/indicators.py` lê e padroniza os microdados, cria classificações e calcula os indicadores.
2. `src/figures.py` transforma as tabelas calculadas em gráficos para análise e apresentação.
3. `src/export_powerbi.py` gera uma tabela-fato em Parquet e uma dimensão de ano para exploração interativa.
4. `docs/RELATORIO.md` reúne metodologia, resultados, limites e conclusões; `docs/POWERBI.md` orienta a montagem do dashboard.

Para conhecer o projeto sem executar o código, comece pelo [relatório analítico](docs/RELATORIO.md). Para explorar os dados de forma interativa, siga o [guia do Power BI](docs/POWERBI.md).

## Estrutura

```
projeto-integrador-II/
├── data/raw/            # zips do INEP + CSVs extraídos por ano
├── data/processed/      # tabela-fato e dimensão de ano para BI
├── outputs/tabelas/     # tabelas de indicadores (CSV, tidy)
├── outputs/figuras/     # visualizações (PNG)
├── docs/RELATORIO.md    # relatório analítico (leitura principal)
└── src/
    ├── config.py        # caminhos, colunas, mapeamentos, filtro de TI
    ├── indicators.py    # ETL + cálculo de indicadores  -> tabelas
    ├── figures.py       # gráficos -> figuras
    └── export_powerbi.py # base tratada -> Parquet/CSV para BI
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
