
---

## 📄 `README.pt-br.md` (Português)

```md
# roma9-data-platform

Plataforma pessoal de dados para análises de longo prazo: pipelines, modelos dbt, NSA/SNA, NLP, LLMs, dashboards e experimentação.

Este repositório é a espinha dorsal da minha plataforma pessoal de dados, reunindo pipelines de ingestão, modelagem analítica com dbt, análises sociais e de redes sociais (NSA/SNA), processamento de linguagem natural (NLP), dashboards e experimentos exploratórios.

## Estrutura principal

- **data-lake/** – dados brutos, refinados e curados (raw → bronze → silver → gold)
- **dbt/** – modelos dbt para transformações e data warehouse semântico
- **analytics/** – análises organizadas por domínio
- **notebooks/** – notebooks exploratórios (NSA, NLP, experimentos)
- **scripts/** – scripts de ingestão, transformação e utilitários

## Objetivos

1. Construir um **data lake** escalável, versionado e de baixo custo  
2. Criar **pipelines e transformações analíticas** com dbt  
3. Realizar **análises de redes sociais (NSA/SNA)** sobre votações e padrões políticos  
4. Aplicar **NLP** em discursos políticos e outros textos  
5. Explorar **LLMs** em contextos analíticos e experimentais  
6. Visualizar resultados por meio de **dashboards**  
7. Manter um **laboratório de dados** de longo prazo para projetos futuros  

## Tecnologias

- Git + GitHub (versionamento e governança)
- Google Cloud Platform (Cloud Storage, BigQuery)
- dbt (transformações, testes e documentação)
- Python (ETL, NLP, NSA/SNA)
- Looker Studio / Power BI (visualização e dashboards)

## Estrutura do repositório

```
roma9-data-platform
├─ analytics
│  ├─ experiments
│  ├─ music
│  ├─ nlp
│  ├─ nsa
│  └─ politics
│     └─ party-territorialization
│        └─ README.md
├─ CONTRIBUTING.md
├─ data-lake
│  ├─ bronze
│  ├─ gold
│  ├─ raw
│  │  └─ README.md
│  └─ silver
├─ dbt
│  ├─ analyses
│  ├─ dbt_project.yml
│  ├─ macros
│  ├─ models
│  │  ├─ common
│  │  ├─ marts
│  │  │  ├─ music
│  │  │  ├─ nlp
│  │  │  ├─ nsa
│  │  │  └─ politics
│  │  │     └─ territorialization
│  │  │        ├─ dimensions
│  │  │        │  └─ dim_territory.sql
│  │  │        ├─ facts
│  │  │        │  └─ fct_votacao_nominal.sql
│  │  │        └─ schema.yml
│  │  └─ staging
│  │     ├─ politics
│  │     │  └─ territorialization
│  │     │     ├─ stg_tse__votacao_nominal.sql
│  │     │     ├─ stg_tse__votacao_nominal.yml
│  │     │     └─ _tse__sources.yml
│  │     └─ stg__healthcheck.sql
│  ├─ package-lock.yml
│  ├─ packages.yml
│  ├─ README.md
│  ├─ seeds
│  ├─ snapshots
│  └─ tests
├─ LICENSE
├─ logs
├─ notebooks
│  ├─ nlp
│  └─ nsa
├─ README.md
└─ scripts
   ├─ ingestion
   │  ├─ politics
   │  │  └─ territorialization
   │  │     ├─ infer_schema_tse.py
   │  │     ├─ load_tse_votacao_nominal.py
   │  │     ├─ load_tse_votacao_nominal_bq.py
   │  │     ├─ load_tse_votacao_nominal_create_table_postgres.py
   │  │     ├─ load_tse_votacao_nominal_create_table_raw_bigquery.sql
   │  │     ├─ load_tse_votacao_nominal_local_csv_postgres.py
   │  │     └─ schema_tse_votacao_nominal.json
   │  └─ README.md
   ├─ transform
   └─ utils
      └─ CREATE_SCHEMA_POSTGRES.sql

```