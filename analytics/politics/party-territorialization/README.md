# Party Territorialization and Fragmentation in Brazil

This project analyzes the territorial distribution of party competition in Brazil,
focusing on the degree of party nationalization and territorial fragmentation
in elections for the Federal Chamber of Deputies.

The analysis covers the period from 2012 to 2024 and is based exclusively on
official electoral data from the Brazilian Superior Electoral Court (TSE).

Status: MVP in progress

## Scope of analysis

- Country: Brazil
- Office: Federal Deputy (Deputado Federal)
- Period: 2012–2024
- Electoral level: State (UF)
- Unit of analysis: Party × State × Election
- Votes considered: Valid nominal votes, 1st round only

## Raw data (TSE)

The electoral data used in this project were obtained directly from the
Brazilian Superior Electoral Court (Tribunal Superior Eleitoral – TSE).

The source files consist of public CSV datasets containing vote counts
at the candidate level, disaggregated by electoral zone and municipality.

The raw data layer is treated as immutable and is preserved without any
logical transformations to ensure auditability and reproducibility.

- Source: TSE public electoral datasets
- Format: CSV
- Coverage: Elections from 2012 to 2024
- Original granularity:
  - Candidate
  - Electoral zone
  - Municipality
  - Election year
- Transformations applied: None

## Data ingestion flow

The ingestion process follows a canonical and reproducible workflow,
independent of the initial exploratory implementation.

1. Download public CSV files from the TSE website
2. Store the original files in Cloud Storage
3. Load the CSV files into BigQuery as raw tables
4. Use the raw BigQuery dataset as the single source of truth
   for all downstream analytical transformations


## Raw layer principles

- The raw dataset is immutable
- No filtering, aggregation, or enrichment is performed at this stage
- All analytical logic is applied only in downstream layers
- The raw layer exists exclusively to preserve data fidelity

```mermaid
graph LR
    TSE[TSE - Public CSV files]
    GCS[Cloud Storage]
    BQ_RAW[BigQuery - Raw dataset]

    TSE --> GCS
    GCS --> BQ_RAW
