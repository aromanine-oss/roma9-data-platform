from pathlib import Path
import pandas as pd
import re
from datetime import datetime
from google.cloud import bigquery

# ==================================================
# CONFIGURAÇÕES
# ==================================================

PROJECT_ID = "roma9-data-platform"
DATASET_ID = "roma9_raw"
TABLE_ID = "tse_votacao_nominal_municipio_zona"

CHUNK_SIZE = 500_000  # ajuste se necessário

# ==================================================
# PATHS
# ==================================================

BASE_DIR = Path(__file__).resolve().parents[4]
DATA_DIR = BASE_DIR / "data" / "tse" / "votacao_nominal_municipio_zona"

if not DATA_DIR.exists():
    raise RuntimeError(f"Pasta de dados não encontrada: {DATA_DIR}")

# ==================================================
# CLIENTE BQ
# ==================================================

bq_client = bigquery.Client(project=PROJECT_ID)
table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

# ==================================================
# FUNÇÕES AUXILIARES
# ==================================================

def extract_year(file_name: str) -> int:
    match = re.search(r'_(\d{4})_', file_name)
    if not match:
        raise ValueError(f"Ano não encontrado no nome do arquivo: {file_name}")
    return int(match.group(1))


# RAW_COLUMNS = [
#     "ANO_ELEICAO",
#     "NR_TURNO",
#     "DS_CARGO",
#     "SG_UF",
#     "CD_MUNICIPIO",
#     "NM_MUNICIPIO",
#     "NR_ZONA",
#     "NR_CANDIDATO",
#     "NM_CANDIDATO",
#     "SG_PARTIDO",
#     "NR_PARTIDO"
# ]

# OPTIONAL_VOTE_COLUMNS = [
#     "QT_VOTOS_NOMINAIS",
#     "QT_VOTOS_NOMINAIS_VALIDOS"
# ]

RAW_SCHEMA_COLUMNS = [
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
    "CD_SITUACAO_DCONST_DIPLOMA"
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
    "NM_TIPO_DESTINACAO_VOTO",
    "QT_VOTOS_NOMINAIS_VALIDOS",
    "CD_SIT_TOT_TURNO",
    "DS_SIT_TOT_TURNO",
    "CD_SITUACAO_DIPLOMA",
    "DS_SITUACAO_DIPLOMA"
]


def load_file(file_path: Path):
    ano_eleicao = extract_year(file_path.name)
    origem_arquivo = file_path.name
    data_carga = datetime.now()

    print(f"\n📥 Iniciando carga: {file_path.name}")

    header = pd.read_csv(
        file_path,
        sep=";",
        encoding="latin1",
        nrows=0
    ).columns.tolist()

    #vote_cols_present = [c for c in OPTIONAL_VOTE_COLUMNS if c in header]

    #usecols = RAW_COLUMNS + vote_cols_present
    usecols = RAW_SCHEMA_COLUMNS


    chunk_iter = pd.read_csv(
        file_path,
        sep=";",
        encoding="latin1",
        #usecols=usecols,
        chunksize=CHUNK_SIZE,
        dtype=str
    )

    total_rows = 0

    for i, chunk in enumerate(chunk_iter, start=1):
        chunk["ANO_ELEICAO"] = ano_eleicao
        chunk["ORIGEM_ARQUIVO"] = origem_arquivo
        chunk["DATA_CARGA"] = data_carga

        # Tipagem mínima (BigQuery cuida do resto)
        # int_cols = [
            # "ANO_ELEICAO",
            # "NR_TURNO",
            # "NR_ZONA",
            # "NR_CANDIDATO",
            # "NR_PARTIDO",
            # "QT_VOTOS_NOMINAIS"
        # ]

        #for col in int_cols:
        #    chunk[col] = pd.to_numeric(chunk[col], errors="coerce")
        #for col in OPTIONAL_VOTE_COLUMNS:
        for col in RAW_SCHEMA_COLUMNS:
            if col not in chunk.columns:
                chunk[col] = None


        job = bq_client.load_table_from_dataframe(
            chunk,
            table_ref,
            job_config=bigquery.LoadJobConfig(
                write_disposition="WRITE_APPEND"
            )
        )

        job.result()  # espera finalizar

        rows = len(chunk)
        total_rows += rows

        print(f"  ✔️ Chunk {i} carregado ({rows:,} linhas)")

    print(f"✅ Arquivo concluído: {total_rows:,} registros carregados")


# ==================================================
# EXECUÇÃO
# ==================================================

def main():
    
    #csv_files = sorted(DATA_DIR.glob("*.csv"))
    csv_files = sorted(DATA_DIR.glob("*.csv"), reverse=True)


    if not csv_files:
        raise RuntimeError("Nenhum CSV encontrado para carga.")

    print(f"📁 Arquivos encontrados: {len(csv_files)}")

    for f in csv_files:
        load_file(f)

    print("\n🎉 Carga finalizada com sucesso.")


if __name__ == "__main__":
    main()
