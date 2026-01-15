from google.cloud import bigquery
from pathlib import Path

# ==================================================
# CONFIGURAÇÕES
# ==================================================

PROJECT_ID = "roma9-data-platform"
DATASET_ID = "roma9_raw"
TABLE_ID = "tse_votacao_nominal_municipio_zona"

GCS_URI = (
    "gs://roma9-data-lake/raw/tse/"
    "votacao_nominal_municipio_zona/votacao_candidato_munzona_2012_BRASIL.csv"
)

SCHEMA_PATH = (
    Path(__file__).parent / "schema_tse_votacao_nominal.json"
)

# ==================================================
# CLIENTE BQ
# ==================================================

client = bigquery.Client(project=PROJECT_ID)

table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

# ==================================================
# LOAD JOB
# ==================================================

job_config = bigquery.LoadJobConfig(
    source_format=bigquery.SourceFormat.CSV,
    skip_leading_rows=1,
    field_delimiter=";",
    encoding="ISO-8859-1",  # latin1
    schema=None,            # será lido do JSON
    write_disposition="WRITE_APPEND",
    allow_quoted_newlines=True,
)

job_config.schema = client.schema_from_json(str(SCHEMA_PATH))

# ==================================================
# EXECUÇÃO
# ==================================================

def main():
    print("🚀 Iniciando carga RAW → BRONZE (BigQuery)")
    print(f"📥 Fonte: {GCS_URI}")
    print(f"📊 Tabela destino: {table_ref}")

    load_job = client.load_table_from_uri(
        source_uris=GCS_URI,
        destination=table_ref,
        job_config=job_config,
    )

    load_job.result()  # espera finalizar

    table = client.get_table(table_ref)
    print(f"✅ Carga finalizada com sucesso!")
    print(f"📈 Total de linhas na tabela: {table.num_rows:,}")


if __name__ == "__main__":
    main()
