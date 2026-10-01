# Dashboard web

Dashboard responsivo em HTML, CSS e JavaScript sobre formação superior em TI e suas implicações para o mercado de trabalho.

## Executar

Na raiz do repositório:

```bash
python -m http.server 8000
```

Acesse <http://localhost:8000/dashboard/>. A conexão com a internet é necessária para carregar o Chart.js e as fontes web.

Os dados exibidos foram derivados dos CSVs de `outputs/tabelas/`. O contexto externo sobre empregos em TIC está identificado e ligado à fonte da Brasscom na própria página.

## Interface e território

O layout utiliza verde, preto e off-white, navegação lateral no desktop e navegação compacta no celular. Os indicadores animam uma vez ao entrar na tela e respeitam `prefers-reduced-motion`.

O mapa usa projeção 3D em Canvas, com extrusão regional, facetas e pontos luminosos. Arraste para girar, clique em uma região ou use os botões acessíveis por teclado. O botão Redefinir restaura a posição inicial. Cor e altura representam o volume de matrículas de 2024; os pontos são textura visual e não localizações de instituições. Os dados de outras métricas regionais não foram adicionados porque não estão na base do dashboard.

As malhas simplificadas estão em `regions.geojson`, obtidas da API oficial do IBGE: `https://servicodados.ibge.gov.br/api/v3/malhas/regioes/{1..5}?formato=application/vnd.geo+json&qualidade=minima`. A geografia é servida localmente, sem chamadas externas durante o uso. Não é necessário instalar dependências ou executar um build.
