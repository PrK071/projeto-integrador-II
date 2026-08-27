# Guia — Dashboard no Power BI

---

## Opção A (recomendada) — Tabela-fato + medidas DAX

Mais flexível: você fatia por ano, região, modalidade, curso, TI, etc., e as taxas se recalculam sozinhas.

### 1. Importar
- Power BI Desktop → **Obter Dados → Parquet** → `data/processed/fato_cursos.parquet` (**20,5 MB**, 1,96M linhas — leve).
- Importe também `data/processed/dim_ano.csv` (dimensão de ano, para cálculos de crescimento).

> Se a sua versão não abrir Parquet, use `data/processed/fato_cursos.csv` (372 MB; o Power BI comprime na importação).

### 2. Modelo
- Relacione **`dim_ano[ANO]` (1) → `fato_cursos[ANO]` (*)**.
- `fato_cursos` já traz as dimensões prontas: `NO_REGIAO`, `SG_UF`, `CATEGORIA`, `REDE`, `NO_CINE_AREA_GERAL`, `NO_CINE_ROTULO`, `GRAU`, `MODALIDADE`, `EH_TI` (valores `TI`/`Outros`).

### 3. Medidas base (colar como novas medidas)

```DAX
Matriculas      = SUM(fato_cursos[QT_MAT])
Ingressantes    = SUM(fato_cursos[QT_ING])
Concluintes     = SUM(fato_cursos[QT_CONC])
Vagas           = SUM(fato_cursos[QT_VG_TOTAL])
Inscritos       = SUM(fato_cursos[QT_INSCRITO_TOTAL])
Base Vinculos   = SUM(fato_cursos[BASE_VINCULOS])
Desvinculados   = SUM(fato_cursos[QT_SIT_DESVINCULADO])
Trancados       = SUM(fato_cursos[QT_SIT_TRANCADA])
Transferidos    = SUM(fato_cursos[QT_SIT_TRANSFERIDO])
IES Distintas   = DISTINCTCOUNT(fato_cursos[CO_IES])
```

### 4. Indicadores (proxies e taxas)

```DAX
Tx Evasao Desvinc % = DIVIDE([Desvinculados], [Base Vinculos])
Tx Evasao Ampla %   = DIVIDE([Desvinculados] + [Trancados] + [Transferidos], [Base Vinculos])
Tx Permanencia %    = DIVIDE([Matriculas], [Base Vinculos])
Conc por Ingr %     = DIVIDE([Concluintes], [Ingressantes])
Rel Candidato Vaga  = DIVIDE([Inscritos], [Vagas])   -- filtrar MODALIDADE = "Presencial"
% Fem = DIVIDE(SUM(fato_cursos[QT_MAT_FEM]), [Matriculas])
```

### 5. Participação e crescimento

```DAX
-- participacao da modalidade (ou de qualquer categoria) no total do ano
% Part Matriculas =
DIVIDE([Matriculas], CALCULATE([Matriculas], ALLSELECTED(fato_cursos[MODALIDADE])))

-- ano anterior (usa dim_ano)
Mat Ano Anterior =
CALCULATE([Matriculas],
    FILTER(ALL(dim_ano), dim_ano[ANO] = MAX(dim_ano[ANO]) - 1))

Crescimento Matriculas % =
DIVIDE([Matriculas] - [Mat Ano Anterior], [Mat Ano Anterior])

-- indice base 2022 = 100
Indice Mat 2022 =
DIVIDE([Matriculas], CALCULATE([Matriculas], ALL(dim_ano), dim_ano[ANO] = 2022)) * 100

-- participacao de TI no total (independe do filtro EH_TI)
% Matriculas TI =
DIVIDE(CALCULATE([Matriculas], fato_cursos[EH_TI] = "TI"), [Matriculas])
```

Formate as taxas como **Porcentagem** (elas retornam fração 0–1).

### 6. Páginas sugeridas (uma por dimensão)

| Página | Visuais | Medidas / campos |
|--------|---------|------------------|
| **Visão geral** | cartões (Matrículas, Ingressantes, % EAD, % TI), filtro de Ano | medidas base + `% Part`, `% Matriculas TI` |
| **D1 Evasão** | linha por Ano (`Tx Evasao Desvinc %`, `Tx Permanencia %`); barras por `MODALIDADE`; mapa por UF | `Tx Evasao *`, `MODALIDADE`, `SG_UF` |
| **D2 EAD vs Presencial** | barras empilhadas `% Part Matriculas` por Ano×Modalidade; linhas de Vagas/Ingressantes | `MODALIDADE`, `dim_ano[ANO]` |
| **D3 Demanda regional** | **Mapa** do Brasil por `NO_REGIAO`/`SG_UF` (Matrículas); barras `Rel Candidato Vaga` (só Presencial) | `NO_REGIAO`, `SG_UF` |
| **D4 TI** | segmentador `EH_TI="TI"`; linha do fluxo TI; ranking `NO_CINE_ROTULO`; barras por Região/Grau/Modalidade; `% Fem` | `% Matriculas TI`, `NO_CINE_ROTULO` |

Para o **mapa**: use o campo `SG_UF` (Power BI reconhece UF do Brasil) ou `NO_UF`; categoria de dados = "Estado/Província".

---

## Opção B (mais simples) — Importar as tabelas prontas

Se não quiser escrever DAX, importe direto os CSVs de `outputs/tabelas/` (já têm as taxas calculadas como coluna) e jogue em visuais simples:

- `d1_evasao_nacional`, `d1_evasao_modalidade` → linhas de evasão
- `d2_modalidade_nacional` → barras de participação (`QT_MAT_PART_PCT`)
- `d3_demanda_regiao`, `d3_demanda_uf` → mapa
- `d4_ti_nacional`, `d4_ti_curso`, `d4_ti_regiao` → TI

Desvantagem: são pré-agregadas, então os filtros cruzados (ex.: evasão de TI só no Nordeste em EAD) **não** funcionam — para isso use a Opção A.

---

## Avisos que valem no dashboard

- **Evasão = proxy transversal** (não coorte). Coloque essa nota num rótulo de texto no dashboard.
- **`Rel Candidato Vaga` só no Presencial** — filtre `MODALIDADE = "Presencial"`, pois vagas de EAD não são regionalizadas no Censo.
- Taxas retornam fração (0–1); formate como porcentagem.
