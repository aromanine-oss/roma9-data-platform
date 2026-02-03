# roma9-data-platform

🇧🇷 Read in Portuguese: [README.pt-br.md](README.pt-br.md)

Personal data platform designed as a long-lived analytical product, not a demo.

This repository represents the backbone of my personal data platform, built to support scalable, versioned, and low-cost analytics over time.
Its core focus is data engineering and analytical modeling, with domain-driven analytical products built on top of a consistent data lake and dbt-based warehouse.

As a concrete example of this platform in action, the repository includes a complete analytical data warehouse built from public CSV data: ingestion, loading, transformation with dbt, and visualization through Looker Studio.
Although intentionally simple (one fact table and a small set of dimensions), this warehouse represents a fully functional, end-to-end analytical product.

## How to navigate this repository

This repository is organized as a long-lived analytical platform, composed of three clearly separated layers: platform foundation, analytical products, and experimentation.

If you are visiting this repository for the first time, the recommended reading path is:

1. **Platform overview (this README)**
2. **Platform foundation**
   - `data-lake/`
   - `scripts/ingestion/`
3. **Analytical foundation (Data Warehouse)**
   - `dbt/`
4. **Delivered analytical product**
   - `analytics/politics/party-territorialization/`
5. **Domain-oriented analytics**
   - `analytics/`
6. **Experiments and research**
   - `notebooks/`, `analytics/experiments/`

## Goals

### Platform (core)
1. Build a scalable, versioned, and low-cost data lake
2. Create reliable pipelines and analytical transformations using dbt
3. Maintain a consistent analytical foundation, validated by a delivered end-to-end data warehouse

### Analytical products
4. Perform social network analysis (NSA/SNA) on voting data and political patterns
5. Apply NLP to political speeches and other textual datasets
6. Visualize analytical results through dashboards and domain-oriented views

### Exploration and experimentation
7. Explore LLMs in analytical and experimental contexts, grounded in real data
8. Maintain a long-term data laboratory for future projects and research

## Current state & roadmap

### Current state
- Layered data lake
- Reproducible ingestion from public CSV sources
- Dimensional data warehouse modeled with dbt
- At least one delivered domain-oriented analytical product
- Dashboards validating end-to-end coherence

### Roadmap
- Expand the warehouse with additional domain-specific marts
- Evolve products with new facts, dimensions, and metrics
- Improve data quality, documentation, and testing
- Explore advanced analytical use cases (NSA, NLP, LLMs) grounded in the platform

```
roma9-data-platform
├─ analytics
│  ├─ experiments
│  ├─ music
│  ├─ nlp
│  ├─ nsa
│  └─ politics
│     └─ party-territorialization
│        ├─ looker-poc
│        │  ├─ painel_looker.png
│        │  ├─ README.md
│        │  └─ vw_votacao_nominal_looker.sql
│        ├─ README.md
│        └─ README.pt-br.md
├─ CONTRIBUTING.md
├─ data-lake
│  ├─ bronze
│  ├─ gold
│  ├─ raw
│  │  ├─ README.md
│  │  └─ README.pt-br.md
│  ├─ README.md
│  ├─ README.pt-br.md
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
│  │  │        │  ├─ dim_candidate.sql
│  │  │        │  ├─ dim_coalition.sql
│  │  │        │  ├─ dim_election.sql
│  │  │        │  ├─ dim_office.sql
│  │  │        │  ├─ dim_party.sql
│  │  │        │  ├─ dim_party_coalition.sql
│  │  │        │  └─ dim_territory.sql
│  │  │        ├─ facts
│  │  │        │  ├─ fct_votacao_nominal.sql
│  │  │        │  └─ int_votacao_nominal.sql
│  │  │        └─ schema.yml
│  │  └─ staging
│  │     ├─ politics
│  │     │  └─ territorialization
│  │     │     ├─ stg_tse.yml
│  │     │     ├─ stg_tse__candidato.sql
│  │     │     ├─ stg_tse__coalizao.sql
│  │     │     ├─ stg_tse__election.sql
│  │     │     ├─ stg_tse__office.sql
│  │     │     ├─ stg_tse__partido.sql
│  │     │     ├─ stg_tse__partido_coalizao.sql
│  │     │     ├─ stg_tse__votacao_nominal.sql
│  │     │     ├─ stg_tse__votacao_nominal.yml
│  │     │     └─ _tse__sources.yml
│  │     └─ stg__healthcheck.sql
│  ├─ package-lock.yml
│  ├─ packages.yml
│  ├─ README.md
│  ├─ README.pt-br.md
│  ├─ seeds
│  ├─ snapshots
│  └─ tests
├─ LICENSE
├─ logs
├─ notebooks
│  ├─ nlp
│  └─ nsa
├─ README.md
├─ README.pt-br.md
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
   │  ├─ README.md
   │  └─ README.pt-br.md
   ├─ transform
   └─ utils
      └─ CREATE_SCHEMA_POSTGRES.sql

```