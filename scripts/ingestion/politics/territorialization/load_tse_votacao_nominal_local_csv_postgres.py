from pathlib import Path
import psycopg2
import re

# ==================================================
# CONFIG
# ==================================================

#DATA_DIR = Path(r"data/tse/votacao_nominal_municipio_zona")
BASE_DIR = Path(__file__).resolve().parents[4]
#DATA_DIR = BASE_DIR / "data" / "tse" / "votacao_nominal_municipio_zona" / "teste"
DATA_DIR = BASE_DIR / "data" / "tse" / "votacao_nominal_municipio_zona"

PG_CONN = {
    "host": "localhost",
    "dbname": "roma9_db",
    "user": "postgres",
    "password": "REMOVIDO",
    "port": 5432,
}

PG_SCHEMA = "staging"
TABLE_PREFIX = "tse_votacao_nominal_municipio_zona"

# ==================================================
# FUNÇÕES
# ==================================================

def extract_year(file_name: str) -> str:
    match = re.search(r'_(\d{4})_', file_name)
    if not match:
        raise ValueError(f"Ano não encontrado no nome do arquivo: {file_name}")
    return match.group(1)


def read_header(csv_path: Path):
    with csv_path.open("r", encoding="latin1") as f:
        raw_header = f.readline().strip()

    columns = []
    for col in raw_header.split(";"):
        col = col.strip()

        # remove aspas duplas extras
        col = col.replace('"', "")

        # remove BOM se existir
        col = col.replace("\ufeff", "")

        # ignora colunas vazias
        if not col:
            continue

        columns.append(col)

    return columns


def create_table_sql(table_name: str, columns: list[str]) -> str:
    cols_sql = ",\n    ".join(f'"{c}" TEXT' for c in columns)

    return f"""
    CREATE TABLE IF NOT EXISTS {PG_SCHEMA}.{table_name} (
        {cols_sql}
    );
    """


def load_csv(cursor, csv_path: Path, table_name: str):
    with csv_path.open("r", encoding="latin1") as f:
        cursor.copy_expert(
            f"""
            COPY {PG_SCHEMA}.{table_name}
            FROM STDIN
            WITH (
                FORMAT csv,
                HEADER true,
                DELIMITER ';',
                QUOTE '"',
                ENCODING 'UTF8'
            )
            """,
            f
        )

# ==================================================
# MAIN
# ==================================================

def main():
    csv_files = sorted(DATA_DIR.glob("*.csv"))

    if not csv_files:
        raise RuntimeError("Nenhum CSV encontrado.")

    conn = psycopg2.connect(**PG_CONN)
    conn.autocommit = False
    cursor = conn.cursor()

    for csv_file in csv_files:
        print(f"\n📥 Processando {csv_file.name}")

        ano = extract_year(csv_file.name)
        table_name = f"{TABLE_PREFIX}_{ano}"

        columns = read_header(csv_file)

        # CREATE TABLE
        ddl = create_table_sql(table_name, columns)
        cursor.execute(ddl)
        conn.commit()

        # COPY
        load_csv(cursor, csv_file, table_name)
        conn.commit()

        print(f"✅ Carga concluída em {PG_SCHEMA}.{table_name}")

    cursor.close()
    conn.close()

    print("\n🎉 Todas as cargas finalizadas com sucesso.")


if __name__ == "__main__":
    main()
