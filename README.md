# roma9-data-platform

Read in Portuguese: [README.pt-br.md](README.pt-br.md)

Personal data platform designed as a long-lived analytical product, not a demo.

This repository represents the backbone of my personal data platform, built to support scalable, versioned, and low-cost analytics over time.
Its core focus is data engineering and analytical modeling, with domain-driven analytical products built on top of a consistent data lake and dbt-based warehouse.

As a concrete example of this platform in action, the repository includes a complete analytical data warehouse built from public CSV data: ingestion, loading, transformation with dbt, and visualization through Looker Studio.
Although intentionally simple (one fact table and a small set of dimensions), this warehouse represents a fully functional, end-to-end analytical product.

## Quickstart

```bash
git clone https://github.com/aromanine-oss/roma9-data-platform.git
cd roma9-data-platform
cd dbt && dbt deps && dbt run && dbt test
```

## Prerequisites

- Python 3.10+
- dbt Core (with your target adapter configured)
- Access to your target warehouse (for example, BigQuery or Postgres)
- Public CSV source files used by ingestion scripts

## Key artifacts

- Delivered analytical product (domain): `analytics/politics/party-territorialization/README.md`
- Looker proof of concept: `analytics/politics/party-territorialization/looker-poc/README.md`
- Looker SQL view: `analytics/politics/party-territorialization/looker-poc/vw_votacao_nominal_looker.sql`
- Main fact model in dbt: `dbt/models/marts/politics/territorialization/facts/fct_votacao_nominal.sql`

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

## Monthly Maintenance Workflow

For ongoing data ingestion and product categorization:

### 1. Load New Invoice Data
```bash
python scripts/misc/nf_data_load_html.py
```

### 2. Check for Unmapped Products
```bash
python scripts/misc/manutencao_produtos.py
```

### 3. Update Product Mappings (if needed)
- **Option A - Interactive CRUD (Recommended)**:
  ```bash
  python scripts/misc/crud_produtos.py
  ```
  Use the interactive menu to add/edit products and categories

- **Option B - Manual SQL Edit**:
  - Edit `scripts/misc/DIM_produtos.sql` to add new canonical products and mappings
  - Apply changes to database

### 4. Validate Coverage
```bash
python scripts/misc/manutencao_produtos.py
```

See `scripts/misc/README_manutencao.md` for detailed maintenance procedures.

## Repository structure

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

