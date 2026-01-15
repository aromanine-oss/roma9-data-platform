from pathlib import Path
import pandas as pd
import re
from collections import defaultdict

# --------------------------------------------------
# Paths (robusto para VS Code aberto em scripts/ingestion)
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[4]
DATA_DIR = BASE_DIR / "data" / "tse" / "votacao_nominal_municipio_zona"

if not DATA_DIR.exists():
    raise RuntimeError(f"Pasta de dados não encontrada: {DATA_DIR}")

# --------------------------------------------------
# Descoberta de arquivos
# --------------------------------------------------

csv_files = sorted(DATA_DIR.glob("*.csv"))

if not csv_files:
    raise RuntimeError("Nenhum arquivo CSV encontrado.")

print(f"📁 Pasta de dados: {DATA_DIR}")
print(f"📄 Arquivos encontrados: {len(csv_files)}")

for f in csv_files:
    print(" -", f.name)

# --------------------------------------------------
# Seleção dos arquivos base para inferência
# --------------------------------------------------
# Estratégia:
# - 1 municipal recente
# - 1 geral recente
# Inferido pelo ano no nome do arquivo
# --------------------------------------------------

def extract_year(file_path: Path) -> int:
    match = re.search(r'_(\d{4})_', file_path.name)
    if not match:
        raise ValueError(f"Ano não encontrado no nome do arquivo: {file_path.name}")
    return int(match.group(1))


files_with_year = [(f, extract_year(f)) for f in csv_files]

# separa municipais (anos pares que não são gerais federais)
municipal_files = [f for f, y in files_with_year if y in {2012, 2016, 2020, 2024}]
general_files   = [f for f, y in files_with_year if y in {2014, 2018, 2022}]

if not municipal_files or not general_files:
    raise RuntimeError("Não foi possível identificar arquivos municipal e geral.")

file_municipal = max(municipal_files)
file_general   = max(general_files)

print("\n🧪 Arquivos usados para inferência:")
print(" - Municipal:", file_municipal.name)
print(" - Geral:    ", file_general.name)

# --------------------------------------------------
# Inferência de schema (somente header)
# --------------------------------------------------

def read_header(file_path: Path) -> set[str]:
    df = pd.read_csv(
        file_path,
        sep=";",
        encoding="latin1",
        nrows=0
    )
    return set(df.columns)

schema_municipal = read_header(file_municipal)
schema_general   = read_header(file_general)

schema_superset = sorted(schema_municipal | schema_general)

print("\n📐 Schema superset inferido:")
for col in schema_superset:
    print(" -", col)

# --------------------------------------------------
# Validação do schema nos demais arquivos
# --------------------------------------------------

print("\n🔍 Validação de schema nos demais arquivos:")

missing_by_file = defaultdict(list)

for file_path in csv_files:
    cols = read_header(file_path)
    missing = set(schema_superset) - cols
    if missing:
        missing_by_file[file_path.name] = sorted(missing)

if not missing_by_file:
    print("✅ Todos os arquivos estão compatíveis com o schema superset.")
else:
    print("⚠️ Diferenças encontradas:")
    for file, missing_cols in missing_by_file.items():
        print(f"\nArquivo: {file}")
        for col in missing_cols:
            print(" -", col)

# --------------------------------------------------
# Saída final
# --------------------------------------------------

print("\n✅ Inferência de schema concluída.")
print(f"Total de colunas no superset: {len(schema_superset)}")
