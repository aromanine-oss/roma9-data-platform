import json
import subprocess

# ---------------------------
# CONFIG
# ---------------------------
BQ_TABLE = "roma9-data-platform:roma9_raw.tse_votacao_nominal_municipio_zona"
PG_SCHEMA = "staging"
PG_TABLE = "tse_votacao_nominal_municipio_zona"

TYPE_MAP = {
    "STRING": "TEXT",
    "INT64": "BIGINT",
    "FLOAT64": "DOUBLE PRECISION",
    "NUMERIC": "NUMERIC",
    "BOOL": "BOOLEAN",
    "DATE": "DATE",
    "TIMESTAMP": "TIMESTAMP",
    "DATETIME": "TIMESTAMP",
    "TIME": "TIME"
}

# ---------------------------
# LÊ SCHEMA DO BIGQUERY
# ---------------------------
BQ_CMD = r"C:/Users/alexr/AppData/Local/Google/Cloud SDK/google-cloud-sdk/bin/bq.cmd"

result = subprocess.run(
    [BQ_CMD, "show", "--schema", "--format=prettyjson", BQ_TABLE],
    capture_output=True,
    text=True,
    check=True
)

schema = json.loads(result.stdout)

# ---------------------------
# GERA COLUNAS
# ---------------------------
columns = []

for field in schema:
    name = field["name"]
    bq_type = field["type"]
    mode = field.get("mode", "NULLABLE")

    if mode == "REPEATED" or bq_type == "RECORD":
        pg_type = "JSONB"
    else:
        pg_type = TYPE_MAP.get(bq_type, "TEXT")

    columns.append(f'    "{name}" {pg_type}')

columns_sql = ",\n".join(columns)

# ---------------------------
# GERA DDL
# ---------------------------
ddl = f"""
DROP TABLE IF EXISTS {PG_SCHEMA}.{PG_TABLE};

CREATE TABLE {PG_SCHEMA}.{PG_TABLE} (
{columns_sql}
);
"""

print(ddl)
