# roma9-data-platform

🇧🇷 Read in Portuguese: [README.pt-br.md](README.pt-br.md)


Personal data platform for lifelong analytics: pipelines, dbt models, NSA/SNA, NLP, LLMs, dashboards, and experimentation.

This repository is the backbone of my personal data platform, bringing together data ingestion pipelines, analytical modeling with dbt, social and social network analysis (NSA/SNA), natural language processing (NLP), dashboards, and exploratory experiments.

## Main structure

- **data-lake/** – raw, refined, and curated data (raw → bronze → silver → gold)
- **dbt/** – dbt models for transformations and semantic data warehouse
- **analytics/** – domain-oriented analytical projects
- **notebooks/** – exploratory notebooks (NSA, NLP, experiments)
- **scripts/** – ingestion, transformation, and utility scripts

## Goals

1. Build a scalable, versioned, and low-cost **data lake**
2. Create reliable **pipelines and analytical transformations** with dbt
3. Perform **social network analysis (NSA/SNA)** on voting data and political patterns
4. Apply **NLP** to political speeches and other textual data
5. Explore **LLMs** in analytical and experimental contexts
6. Visualize results through **dashboards**
7. Maintain a long-term **data laboratory** for future projects and research

## Technologies

- Git + GitHub (version control and governance)
- Google Cloud Platform (Cloud Storage, BigQuery)
- dbt (transformations, tests, and documentation)
- Python (ETL, NLP, NSA/SNA)
- Looker Studio / Power BI (dashboards and visualization)

## Repository structure
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
