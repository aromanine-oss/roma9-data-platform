from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime

# ==================================================
# CONFIG
# ==================================================

PG_SCHEMA = "staging"
PG_TABLE = "tse_votacao_nominal_municipio_zona"

ENGINE_URL = (
    "postgresql+psycopg2://postgres:REMOVIDO"
    "@localhost:5432/roma9_db"
)

CHUNK_SIZE = 200_000
DELIMITER = ";"
ENCODING = "latin1"

# ==================================================
# PATH
# ==================================================

BASE_DIR = Path(__file__).resolve().parents[4]
#DATA_DIR = BASE_DIR / "data" / "tse" / "votacao_nominal_municipio_zona" / "teste"
DATA_DIR = BASE_DIR / "data" / "tse" / "votacao_nominal_municipio_zona"

# ==================================================
# SCHEMA CANÔNICO
# ==================================================

CSV_COLUMNS = [
    "HH_GERACAO",
    "ANO_ELEICAO",
    "CD_TIPO_ELEICAO",
    "NM_TIPO_ELEICAO",
    "NR_TURNO",
    "CD_ELEICAO",
    "DS_ELEICAO",
    "DT_ELEICAO",
    "TP_ABRANGENCIA",
    "SG_UF",
    "SG_UE",
    "NM_UE",
    "CD_MUNICIPIO",
    "NM_MUNICIPIO",
    "NR_ZONA",
    "DS_CARGO",
    "SQ_CANDIDATO",
    "NR_CANDIDATO",
    "NM_CANDIDATO",
    "NM_URNA_CANDIDATO",
    "NM_SOCIAL_CANDIDATO",
    "CD_SITUACAO_CANDIDATURA",
    "DS_SITUACAO_CANDIDATURA",
    "CD_DETALHE_SITUACAO_CAND",
    "DS_DETALHE_SITUACAO_CAND",
    "CD_SITUACAO_JULGAMENTO",
    "DS_SITUACAO_JULGAMENTO",
    "CD_SITUACAO_CASSACAO",
    "DS_SITUACAO_CASSACAO",
    "CD_SITUACAO_DCONST_DIPLOMA",
    "DS_SITUACAO_DCONST_DIPLOMA",
    "TP_AGREMIACAO",
    "NR_PARTIDO",
    "SG_PARTIDO",
    "NM_PARTIDO",
    "NR_FEDERACAO",
    "NM_FEDERACAO",
    "SG_FEDERACAO",
    "DS_COMPOSICAO_FEDERACAO",
    "SQ_COLIGACAO",
    "NM_COLIGACAO",
    "DS_COMPOSICAO_COLIGACAO",
    "ST_VOTO_EM_TRANSITO",
    "QT_VOTOS_NOMINAIS",
    "NM_TIPO_DESTINACAO_VOTOS",
    "QT_VOTOS_NOMINAIS_VALIDOS",
    "CD_SIT_TOT_TURNO",
    "DS_SIT_TOT_TURNO",
    "CD_SITUACAO_DIPLOMA",
    "DS_SITUACAO_DIPLOMA"
]

# ==================================================
# CARGA
# ==================================================

def load_file(file_path: Path, engine):
    origem_arquivo = file_path.name
    data_carga = datetime.now()

    print(f"\n📥 Iniciando carga: {origem_arquivo}")

    chunk_iter = pd.read_csv(
        file_path,
        sep=DELIMITER,
        encoding=ENCODING,
        dtype=str,
        chunksize=CHUNK_SIZE
    )

    total = 0

    for i, chunk in enumerate(chunk_iter, start=1):
        # adiciona colunas faltantes
        for col in CSV_COLUMNS:
            if col not in chunk.columns:
                chunk[col] = None

        # remove colunas extras
        chunk = chunk[CSV_COLUMNS].copy()

        # metadados
        chunk.loc[:, "ORIGEM_ARQUIVO"] = origem_arquivo
        chunk.loc[:, "DATA_CARGA"] = data_carga

        chunk.to_sql(
            PG_TABLE,
            engine,
            schema=PG_SCHEMA,
            if_exists="append",
            index=False,
            method="multi"
        )

        total += len(chunk)
        print(f"  ✔️ Chunk {i} ({len(chunk):,} linhas)")

    print(f"✅ Arquivo concluído: {total:,} registros")


def main():
    csv_files = sorted(DATA_DIR.glob("*.csv"), reverse=True)

    if not csv_files:
        raise RuntimeError("Nenhum CSV encontrado.")

    engine = create_engine(ENGINE_URL)

    print(f"📁 Arquivos encontrados: {len(csv_files)}")

    for f in csv_files:
        try:
            load_file(f, engine)
        except Exception as e:
            print(f"❌ Erro em {f.name}: {e}")

    print("\n🎉 Carga finalizada com sucesso.")


if __name__ == "__main__":
    main()
