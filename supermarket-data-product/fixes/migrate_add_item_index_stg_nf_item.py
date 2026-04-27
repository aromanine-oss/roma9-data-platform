from pathlib import Path
import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[1]

PG_CONN = {
    "host": os.getenv("DB_HOST"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASS"),
    "port": int(os.getenv("DB_PORT", 5432)),
}

PG_SCHEMA = "staging"
TABLE_NAME = "stg_nf_item"
INDEX_NAME = "idx_stg_nf_item_id_nota_item_index"


def validate_pg_conn():
    missing = [key for key, value in PG_CONN.items() if value is None]
    if missing:
        raise EnvironmentError(f"Missing Postgres env vars: {', '.join(missing)}")


def main():
    validate_pg_conn()
    conn = psycopg2.connect(**PG_CONN)
    conn.autocommit = False
    cursor = conn.cursor()

    cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {PG_SCHEMA};")
    cursor.execute(
        f"ALTER TABLE {PG_SCHEMA}.{TABLE_NAME} ADD COLUMN IF NOT EXISTS item_index INTEGER;"
    )

    cursor.execute(
        f"WITH numbered AS ("
        f" SELECT ctid AS rowid, row_number() OVER (PARTITION BY id_nota "
        f" ORDER BY produto, codigo_produto, quantidade, valor_unit, valor_total) AS rn "
        f" FROM {PG_SCHEMA}.{TABLE_NAME}) "
        f"UPDATE {PG_SCHEMA}.{TABLE_NAME} "
        f"SET item_index = numbered.rn "
        f"FROM numbered "
        f"WHERE {PG_SCHEMA}.{TABLE_NAME}.ctid = numbered.rowid;"
    )

    cursor.execute(
        f"CREATE UNIQUE INDEX IF NOT EXISTS {INDEX_NAME} "
        f"ON {PG_SCHEMA}.{TABLE_NAME} (id_nota, item_index);"
    )

    conn.commit()
    cursor.close()
    conn.close()

    print(f"✅ Migração concluída: coluna item_index adicionada e preenchida em {PG_SCHEMA}.{TABLE_NAME}.")
    print(f"✅ Índice único {INDEX_NAME} criado para prevenir duplicações.")


if __name__ == "__main__":
    main()
