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
