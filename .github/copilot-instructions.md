# Copilot Instructions for roma9-data-platform

This repository is a long-lived analytical platform with a layered data lake, dbt modeling, and a delivered domain product.

- Treat the repository as a platform, not a one-off demo.
- Core flow: `data/` → ingestion scripts → `staging` / data lake → `dbt/` transformations → `analytics/` products.
- Key directories:
  - `scripts/ingestion/`: ingestion and raw-loading code for CSV/HTML/PDF into Postgres staging.
  - `dbt/`: analytical modeling layer, including `models/`, `macros/`, `tests/`, and `schema.yml` documentation.
  - `analytics/politics/party-territorialization/`: reference analytical product and domain example.
- Use Python 3.10+ and the repo virtual environment if present. There is no locked dependency manifest, so preserve existing imports and avoid adding unsupported packages.

## Important repository patterns

- dbt conventions:
  - `dbt/models/staging/` are staging views.
  - `dbt/models/marts/` are business marts and tables.
  - `int_` models are intermediate tables.
  - `dim_` and `fct_` models are dimensions and facts.
- `dbt/dbt_project.yml` sets `profile: 'roma9_data_platform'` and global materializations for `staging`/`marts`/`int`.
- Ingestion scripts use `dotenv` to load Postgres credentials: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASS`, `DB_PORT`.
- Staging scripts usually create tables in `staging` schema and then load raw data via `psycopg2`.
- Ingestion examples:
  - `scripts/ingestion/politics/territorialization/load_tse_votacao_nominal_local_csv_postgres.py`
  - `scripts/misc/nf_data_load_html.py`

## Workflow guidance

- The canonical run command is in `README.md`: `cd dbt && dbt deps && dbt run && dbt test`.
- Do not assume a repo-local `profiles.yml` exists; dbt profile configuration is external.
- Keep model SQL changes inside `dbt/` and documentation in adjacent `schema.yml` files.

## Editing guidance

- Keep changes aligned with the layered architecture: raw ingestion → staging → analytical modeling → product.
- Prefer explicit dbt SQL models over ad hoc transformations in arbitrary scripts.
- When extending ingestion, follow existing script structure and use `scripts/ingestion/` as the source-of-truth for new raw sources.
- Use `analytics/politics/party-territorialization/README.md` to understand domain intent and product scope.

## Do not change

- Do not modify notebooks or experimental artifacts under `notebooks/` and `analytics/experiments/` unless there is a clear platform requirement.
- Do not change `dbt/dbt_project.yml` profile settings or materialization conventions without confirming the existing dbt design.
- Do not alter the conceptual `data-lake/` layer structure (`raw/`, `bronze/`, `silver/`, `gold/`) unless adding a compatible extension.

## Repo-specific notes

- The issue template `.github/ISSUE_TEMPLATE/analytics-engineering.md` expects `dbt run/test verde`, YAML documentation, and clear model scoping.
- `data-lake/` is a conceptual storage foundation with `raw/`, `bronze/`, `silver/`, and `gold/` layers.
- Avoid introducing broad architecture changes unless necessary to support the existing data lake / dbt product orientation.
