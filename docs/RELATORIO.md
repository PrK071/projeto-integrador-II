# Panorama do Ensino Superior Brasileiro: Evasão, Modalidades de Ensino e a Expansão dos Cursos de TI

**Fonte:** Microdados do Censo da Educação Superior (INEP) — arquivo *Cadastro de Cursos*, edições **2022, 2023 e 2024**.
**Cobertura:** 1.964.978 registros curso-ano (todos os cursos de graduação do país nos três anos).
**Elaboração:** pipeline reproduzível em Python (`src/`), tabelas em `outputs/tabelas/`, figuras em `outputs/figuras/`.

---

## 1. Nota metodológica (leia antes dos resultados)

O arquivo utilizado é o **Cadastro de Cursos**, que traz **contagens agregadas por curso** (matrículas, ingressantes, concluintes, vagas, inscritos, situação de vínculo e recortes demográficos). **Não** utilizamos o módulo Aluno (dado nominal), hoje disponível apenas via SEDAP mediante solicitação.

Classificação de cada indicador:

| Tipo | Exemplos neste relatório |
|------|--------------------------|
| **Dado direto do Censo** | `QT_MAT`, `QT_ING`, `QT_CONC`, `QT_VG_TOTAL`, `QT_INSCRITO_TOTAL`, `QT_SIT_*` |
| **Indicador calculado** | participação % por modalidade, crescimento anual %, índice base 2022=100, relação candidato/vaga |
| **Proxy / estimativa** | taxas de evasão, retenção e permanência (ver abaixo) |
| **Interpretação** | comentários de cada seção |

**Definições oficiais (dicionário INEP 2024) que estruturam os proxies de evasão:**

- `QT_MAT` = alunos com vínculo **"Cursando e/ou Formado"**. **Não** inclui trancados, desvinculados, transferidos nem falecidos.
- `QT_SIT_TRANCADA`, `QT_SIT_DESVINCULADO`, `QT_SIT_TRANSFERIDO`, `QT_SIT_FALECIDO` = contagens de vínculo **separadas** de `QT_MAT`.

Logo, definimos o **universo de vínculos do ano**:

```
BASE_VINCULOS = QT_MAT + QT_SIT_TRANCADA + QT_SIT_DESVINCULADO + QT_SIT_TRANSFERIDO + QT_SIT_FALECIDO
```

E os **proxies transversais**:

- **Taxa de evasão (desvinculação)** = `QT_SIT_DESVINCULADO / BASE_VINCULOS`
- **Taxa de trancamento** = `QT_SIT_TRANCADA / BASE_VINCULOS`
- **Taxa de evasão ampla** = `(DESVINCULADO + TRANCADA + TRANSFERIDO) / BASE_VINCULOS`
- **Taxa de permanência** = `QT_MAT / BASE_VINCULOS`

> ⚠️ **Limite:** o Censo é um **retrato transversal anual**. Estes proxies medem a *composição* dos vínculos em cada ano, **não** a evasão de uma coorte acompanhada ao longo do tempo. Uma taxa de evasão longitudinal exigiria o módulo Aluno nominal. Toda leitura de "evasão" abaixo é comparativa/estrutural, não causal.

Comparabilidade entre anos: das 25 variáveis-chave, **todas existem nas três edições**. As únicas diferenças de estrutura estão em colunas de detalhamento de reserva de vagas (`QT_*_RV*`), não usadas aqui.

---

## 2. Dimensão 1 — Evasão e retenção

*(tabelas `d1_*`; figuras `d1_evasao_nacional.png`, `d1_evasao_modalidade.png`)*

| Ano | Matrículas | Evasão (desvinc.) | Evasão ampla | Permanência |
|-----|-----------:|------------------:|-------------:|------------:|
| 2022 | 9.444.116 | 20,90% | 34,40% | 65,59% |
| 2023 | 9.977.217 | 21,15% | 34,33% | 65,65% |
| 2024 | 10.227.266 | 22,55% | 34,93% | 65,06% |

**O que aconteceu:** a taxa de desvinculação (proxy de evasão) **subiu de 20,9% para 22,6%** entre 2022 e 2024; a permanência recuou levemente (65,6% → 65,1%).

**Diferença por modalidade (o achado mais forte):**

| Ano | Evasão EAD | Evasão Presencial | Concluintes/Ingressantes EAD | Concl./Ingr. Presencial |
|-----|-----------:|------------------:|-----------------------------:|------------------------:|
| 2022 | 26,2% | 15,5% | 15,6% | 48,5% |
| 2024 | 28,4% | 14,8% | 18,1% | 43,9% |

- A evasão no **EAD é ~2x a do presencial** e a distância **aumentou** (26,2%→28,4% no EAD; queda no presencial).
- A relação concluintes/ingressantes é muito menor no EAD, coerente com maior desvinculação.

**Conclusão possível:** o crescimento da evasão nacional é puxado pela **expansão do EAD, modalidade com desvinculação estruturalmente maior**. **Não é possível** afirmar causa (perfil do aluno, trabalho, autodisciplina, qualidade) só com estes dados.

---

## 3. Dimensão 2 — EAD vs. Presencial

*(tabela `d2_modalidade_nacional`; figuras `d2_*`)*

| Ano | Mod. | Vagas | Ingressantes | Matrículas | Concluintes | IES | % matríc. |
|-----|------|------:|-------------:|-----------:|------------:|----:|----------:|
| 2022 | EAD | 17.171.895 | 3.100.556 | 4.330.934 | 483.834 | 645 | 45,9% |
| 2024 | EAD | 18.590.273 | 3.347.573 | 5.189.391 | 604.742 | 793 | **50,7%** |
| 2022 | Presencial | 5.658.590 | 1.656.401 | 5.113.182 | 803.801 | 2.533 | 54,1% |
| 2024 | Presencial | 5.075.146 | 1.663.040 | 5.037.875 | 729.246 | 2.444 | 49,3% |

**Marco histórico:** em **2024 o EAD ultrapassou o presencial em matrículas** (50,7% vs. 49,3%). Em **ingressantes**, o EAD já é **~2x** o presencial (3,35 mi vs. 1,66 mi).

**O crescimento do EAD vem de quê?** Matrículas EAD +19,8% (2022→2024) e ingressantes +8,0%, enquanto **vagas** oscilam num patamar altíssimo (~17–19 mi, contra ~1,66 mi de ingressantes). Ou seja, o gargalo **não é oferta de vaga** — há enorme capacidade ociosa; o crescimento vem da **conversão de ingresso/matrícula**, não de abertura de vagas. O presencial está **estagnado/recuando** em todos os fluxos.

**IES ofertantes:** o EAD saltou de 645 para 793 instituições (+22,9%); o presencial caiu de 2.533 para 2.444.

---

## 4. Dimensão 3 — Demanda e distribuição regional

*(tabelas `d3_*`, `d2_modalidade_regiao`; figuras `d3_*`)*

Matrículas por região (2024) e crescimento da procura (inscritos) 2022→2024:

| Região | Matrículas 2024 | Relação candidato/vaga (presencial) |
|--------|----------------:|------------------------------------:|
| Sudeste | 4.518.942 | 1,75 |
| Nordeste | 2.186.521 | 1,71 |
| Sul | 1.750.161 | 1,58 |
| Centro-Oeste | 905.093 | 1,67 |
| Norte | 863.969 | 1,68 |

> **Nota metodológica importante:** as **vagas de EAD não são regionalizadas** no cadastro (aparecem sem UF/região — linha "NaN" nas tabelas, ~18 mi de vagas). Por isso a **relação candidato/vaga só é interpretável no presencial**. As matrículas, essas sim, são regionalizadas e confiáveis para todas as modalidades.

**O que aconteceu:** o **Sudeste concentra a demanda** (≈45% das matrículas e da procura nacional). A relação candidato/vaga presencial é baixa em todas as regiões (1,5–1,8 inscrito por vaga), refletindo grande oferta.

---

## 5. Dimensão 4 — Expansão dos cursos de TI

**Recorte (classificação derivada):** área geral CINE **6 — Computação e TIC** *mais* o rótulo **"Engenharia de computação"** (que o CINE aloca na área 7 — Engenharia). Documentado em `src/config.py::eh_ti`. *Licenciatura em Computação* (área Educação) foi **deixada de fora** por ser formação de professores.

*(tabelas `d4_*`; figuras `d4_*`)*

### 5.1 Crescimento e participação

| Ano | Matríc. TI | Ingr. TI | Concl. TI | % matríc. no total | % ingr. no total |
|-----|-----------:|---------:|----------:|-------------------:|-----------------:|
| 2022 | 633.688 | 425.216 | 64.486 | 6,71% | 8,94% |
| 2024 | 860.791 | 509.828 | 106.157 | **8,42%** | 10,17% |

- Matrículas de TI **+35,8%** em dois anos, contra **+8,3%** do ensino superior total → **TI cresce ~4x mais rápido** e **ganha participação** (6,7%→8,4%).
- Concluintes de TI **+64,6%** (64,5k→106,2k), crescendo **mais rápido que os ingressantes** (+19,9%) — a formação está "amadurecendo", com turmas que ingressaram antes agora concluindo.

### 5.2 Cursos que mais cresceram (índice base 2022=100, matrículas 2024)

| Curso | Matríc. 2024 | Índice 2024 (2022=100) |
|-------|-------------:|-----------------------:|
| Inteligência artificial | 3.250 | 821 |
| Interdisciplinares em TIC | 14.735 | 444 |
| Defesa cibernética | 10.547 | 192 |
| Engenharia de software | 69.832 | 188 |
| Ciência da computação | 127.190 | 136 |
| Sistemas de informação | 420.479 | 136 |
| Gestão da TI | 59.647 | 121 |

Os **maiores em volume** são Sistemas de Informação (420k) e Ciência da Computação (127k); os de **crescimento explosivo** são os emergentes (IA, cibersegurança, interdisciplinares), ainda pequenos em base.

### 5.3 Modalidade, região e perfil

- **Modalidade:** EAD em TI 350k→504k (**+43,9%**); presencial 283k→357k (**+26,0%**). O crescimento de TI é **majoritário e mais acelerado no EAD**.
- **Grau:** predomínio de cursos **Tecnológicos** (505k em 2024) sobre Bacharelado (356k); concluintes tecnológicos crescem forte (44,6k→77,5k).
- **Região (matrículas TI, crescimento 2022→2024):** Centro-Oeste **+43,6%**, Nordeste **+40,5%**, Sudeste +35,1%, Norte +34,5%, Sul +30,3%. **Sudeste lidera em volume** (448,7k); **Centro-Oeste e Nordeste lideram em ritmo**.
- **Sexo:** forte predomínio **masculino (~81%)**; participação feminina sobe lentamente (17,7%→18,9%).
- **Idade:** concentração na faixa **18–24 anos**, em expansão.

---

## 6. Cruzamento dos resultados

1. **Evasão × EAD:** a evasão nacional sobe porque o EAD — modalidade de maior desvinculação — vira maioria. TI acompanha o padrão (evasão ~21–23%, próxima da média nacional).
2. **TI × modalidade:** TI é puxado pelo EAD, exatamente a modalidade de maior evasão → **risco de gargalo na formação efetiva** de profissionais, apesar do ingresso alto.
3. **TI × região:** o crescimento mais rápido está em regiões de menor base (Centro-Oeste, Nordeste) — sinal de **interiorização/capilarização** da oferta de TI, mas o volume segue concentrado no Sudeste.

---

## 7. Resolução da pendência do professor — "Identificar a demanda por mercado e região"

O comentário do professor pede **especificar a(s) região(ões)**. Com base nos dados, a recomendação objetiva é:

- **Região-foco principal: Sudeste.** Concentra ~45% da demanda nacional e o **maior mercado de TI** (448,7 mil matrículas em 2024), sendo a referência para "demanda por mercado".
- **Regiões-foco de expansão (comparativo): Nordeste e Centro-Oeste.** Apresentam o **maior crescimento de TI** no período (+40,5% e +43,6%), evidenciando **capilarização** da formação tecnológica para fora do eixo tradicional.

**Objetivo reescrito (sugestão para reenvio):**
> *"Identificar a demanda por cursos de TI e sua distribuição regional, tomando como recorte principal a região **Sudeste** (maior mercado em volume) e, em caráter comparativo, as regiões **Nordeste** e **Centro-Oeste** (maiores taxas de crescimento), a fim de contrastar concentração de mercado e expansão/interiorização da oferta."*

---

## 8. Conclusões

- A evasão (proxy) **aumentou** (20,9%→22,6%), puxada pela **transição para o EAD**, cuja desvinculação é ~2x a presencial.
- 2024 marca a **virada do EAD**, agora maioria das matrículas e dominante em ingressantes; o crescimento vem de **conversão de ingresso**, não de novas vagas (há grande ociosidade de vagas EAD).
- A demanda é **concentrada no Sudeste**; a relação candidato/vaga presencial é baixa (1,5–1,8).
- **TI é o segmento mais dinâmico**: cresce ~4x mais que o total, ganha participação, forma cada vez mais concluintes, com destaque para IA, cibersegurança e Engenharia de Software. Perfil ainda muito masculino e majoritariamente EAD/tecnológico.

**O que os dados NÃO permitem afirmar:** causas da evasão, qualidade dos cursos, inserção no mercado de trabalho e evasão de coorte real (exigiria dado longitudinal/nominal). Correlações observadas **não implicam causalidade**.
