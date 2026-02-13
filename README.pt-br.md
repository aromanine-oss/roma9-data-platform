# roma9-data-platform

Read in English: [README.md](README.md)

Plataforma pessoal de dados projetada como um produto analitico de longo prazo, nao como uma demo.

Este repositorio representa a espinha dorsal da minha plataforma pessoal de dados, construida para suportar analises escalaveis, versionadas e de baixo custo ao longo do tempo.
Seu foco principal e engenharia de dados e modelagem analitica, com produtos analiticos orientados a dominio construidos sobre um data lake consistente e um data warehouse com dbt.

Como exemplo concreto da plataforma em funcionamento, o repositorio inclui um data warehouse analitico completo construido a partir de dados publicos em CSV: ingestao, carga, transformacao com dbt e visualizacao no Looker Studio.
Embora intencionalmente simples (uma tabela fato e um pequeno conjunto de dimensoes), esse warehouse representa um produto analitico ponta a ponta totalmente funcional.

## Inicio rapido

```bash
git clone https://github.com/aromanine-oss/roma9-data-platform.git
cd roma9-data-platform
cd dbt && dbt deps && dbt run && dbt test
```

## Pre-requisitos

- Python 3.10+
- dbt Core (com o adaptador do seu target configurado)
- Acesso ao seu data warehouse de destino (por exemplo, BigQuery ou Postgres)
- Arquivos CSV publicos usados pelos scripts de ingestao

## Artefatos principais

- Produto analitico entregue (dominio): `analytics/politics/party-territorialization/README.pt-br.md`
- Prova de conceito no Looker: `analytics/politics/party-territorialization/looker-poc/README.md`
- View SQL do Looker: `analytics/politics/party-territorialization/looker-poc/vw_votacao_nominal_looker.sql`
- Modelo fato principal no dbt: `dbt/models/marts/politics/territorialization/facts/fct_votacao_nominal.sql`

## Como navegar neste repositorio

Este repositório é organizado como uma plataforma analítica de longo prazo, composta por três camadas bem definidas: fundação da plataforma, produtos analíticos e experimentação.

Para quem está visitando o projeto pela primeira vez, o caminho de leitura recomendado é:

1. **Visão geral da plataforma (este README)**
2. **Fundação da plataforma**
   - `data-lake/`
   - `scripts/ingestion/`
3. **Fundação analítica (Data Warehouse)**
   - `dbt/`
4. **Produto analítico entregue**
   - `analytics/politics/party-territorialization/`
5. **Análises orientadas a domínio**
   - `analytics/`
6. **Experimentos e pesquisa**
   - `notebooks/`, `analytics/experiments/`

## Objetivos

### Plataforma (core)
1. Construir um data lake escalável, versionado e de baixo custo
2. Criar pipelines confiáveis e transformações analíticas com dbt
3. Manter uma fundação analítica consistente, validada por um data warehouse ponta a ponta entregue

### Produtos analíticos
4. Realizar análises de redes sociais (NSA/SNA) sobre dados de votação e padrões políticos
5. Aplicar NLP a discursos políticos e outros conjuntos textuais
6. Visualizar resultados analíticos por meio de dashboards

### Exploração e experimentação
7. Explorar LLMs em contextos analíticos e experimentais, ancorados em dados reais
8. Manter um laboratório de dados de longo prazo para projetos futuros e pesquisa

## Estado atual e roadmap

### Estado atual
- Data lake em camadas
- Ingestão reproduzível a partir de CSVs públicos
- Data warehouse dimensional modelado com dbt
- Pelo menos um produto analítico orientado a domínio já entregue
- Dashboards validando a coerência ponta a ponta

### Roadmap
- Expandir o warehouse com novos marts orientados a domínio
- Evoluir produtos com novos fatos, dimensões e métricas
- Aprimorar qualidade de dados, documentação e testes
- Explorar casos analíticos avançados (NSA, NLP, LLMs) ancorados na plataforma

```text
roma9-data-platform/
|- analytics/
|  |- experiments/
|  |- music/
|  |- nlp/
|  |- nsa/
|  `- politics/
|     `- party-territorialization/
|- data-lake/
|  |- raw/
|  |- bronze/
|  |- silver/
|  `- gold/
|- dbt/
|  |- models/
|  |- macros/
|  |- seeds/
|  |- snapshots/
|  `- tests/
|- notebooks/
|- scripts/
|  |- ingestion/
|  |- transform/
|  `- utils/
|- README.md
`- README.pt-br.md
```

