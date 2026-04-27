from difflib import SequenceMatcher
from pathlib import Path
import os
import re
import unicodedata

from bs4 import BeautifulSoup
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# ==================================================
# CONFIG
# ==================================================

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data" / "Notas Fiscais" / "2026" / "abr"

PG_CONN = {
    "host": os.getenv("DB_HOST"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASS"),
    "port": int(os.getenv("DB_PORT", 5432)),
}

PG_SCHEMA = "staging"
TABLE_NAME = "stg_nf_item"
HEADER_TABLE_NAME = "stg_nf_header"
PRODUTO_STAGING_TABLE = "stg_produtos"
ITEM_INDEX_NAME = "idx_stg_nf_item_id_nota_item_index"
SIMILARITY_THRESHOLD = 0.82
DESCRIPTION_CANONICAL_OVERRIDES = {
    "AREIA GATOS KAT BOM 3KG CLINICAL": "Areia para Gatos",
    "BEB CRYSTAL LIMAO C GAS 510ML": "Água Saborizada Crystal",
    "AGUA SAB AGUA DA PEDRA LIM ALE C G 350ML": "Água Saborizada Água Pedra",
    "AGUA SAB AGUA DA PEDRA ABA HOR C G 350ML": "Água Saborizada Água Pedra",
    "AGUA SAB AGUA DA PEDRA BER CAP C G 350ML": "Água Saborizada Água Pedra",
    "AGUA SAB AGUA DA PEDRA BLUE LI C G 350ML": "Água Saborizada Água Pedra",
    "AGUA SAB AGUA DA PEDRA F VERM C G 350ML": "Água Saborizada Água Pedra",
    "AGUA TONICA ANTARCTICA LT 350ML": "Água Tônica Schweppes",
    "AGUA TONICA FYS ZERO LT 350ML": "Água Tônica Schweppes",
    "BEB CRYSTAL FRUTAS VERMELHAS C GAS 510ML": "Água Saborizada Crystal",
    "DETERG AZULIM NEUTRO FR 500ML": "Detergente",
    "ESCOVA BETANIN NOVICA ADAPT 114 UN": "Escova de dente",
    "GOMA MASCAR TRIDENT MAX COOL S A 16.5G": "Chicletes",
    "GOMA MASCAR TRIDENT X GAM CITR S A 48.3G": "Chicletes",
    "LIMP CIF ESPUMA MILAG EXT LIMO C C 500ML": "Tira Limo",
    "MACA FUJI KG": "Maçã",
    "MIX SALADA BERTOLIN PREMIUM UN": "Mix Salada",
    "ORGANIZADOR CLEAR ACASA B 22X9 PEQ EP435": "Organizador Clear",
    "ORGANIZADOR CLEAR ACASA B 36X15 M EP 611": "Organizador Clear",
    "OVO VERMELHO IANA GRANDE C 30": "Ovo de Galinha Vermelho",
    "PASSATA TOM LA MOLISANA CLASSICA VD 690G": "Passata de Tomate",
    "PERA D ANJOU IMPORTADA KG": "Pera",
    "PRESUNTO COZIDO FATIADO SADIA KG": "Presunto",
    "RODO PIA ARTICULAVEL ACASA BAMBU PT 590D": "Rodo de Pia",
    "AGUA MINERAL AGUA PURA C GAS PET 500ML": "Água Mineral",
    "TOMATE LA CAMPAGNOLA S PELE LT 240G": "Tomate pelado",
    "AGUA MINERAL AGUA PURA S GAS PET 5L": "Água Mineral",
}


# ==================================================
# HELPERS
# ==================================================

def get_text(node):
    return node.get_text(strip=True) if node else None


def validate_pg_conn():
    missing = [key for key, value in PG_CONN.items() if value is None]
    if missing:
        raise EnvironmentError(f"Missing Postgres env vars: {', '.join(missing)}")


def validate_data_emissao(header, html_path: Path):
    data_emissao = header[3]
    if not data_emissao or not data_emissao.strip():
        print(f"data_emissao nao extraida para {html_path}")
        return False
    return True


def normalize_text(value):
    if not value:
        return ""
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.upper().strip()
    value = re.sub(r"\s+", " ", value)
    return value


def simplify_product_text(value):
    value = normalize_text(value)
    if not value:
        return ""

    # Remove ruídos comuns de descrição fiscal para aproximar do nome canônico.
    noise_patterns = [
        r"\bPROMOCAO\b",
        r"\bPROM\b",
        r"\bOFERTA\b",
        r"\bUN\b",
        r"\bUND\b",
        r"\bLATA\b",
        r"\bLT\b",
        r"\bLONG NECK\b",
        r"\bLN\b",
        r"\bPET\b",
        r"\bGF\b",
        r"\bGARRAFA\b",
        r"\bSLEEK\b",
        r"\bCX\b",
        r"\bCXS?\b",
        r"\bPCT\b",
        r"\bFR\b",
        r"\bTP\b",
        r"\bVD\b",
        r"\bVIDRO\b",
        r"\bZERO ACUCAR\b",
        r"\bSEM ACUCAR\b",
        r"\bCOM GAS\b",
        r"\bSEM GAS\b",
        r"\bCGAS\b",
        r"\bSGAS\b",
        r"\bORI(GINAL)?\b",
        r"\bEXTRA\b",
        r"\bPURO MALTE\b",
        r"\bTRAD(ICIONAL)?\b",
        r"\bPACK\b",
        r"\bC\d+\b",
        r"\b\d+[.,]?\d*\s*(ML|L|KG|G|MG)\b",
        r"\b\d+[.,]?\d*\b",
    ]

    for pattern in noise_patterns:
        value = re.sub(pattern, " ", value)

    value = re.sub(r"\s+", " ", value).strip()
    return value


def get_preferred_canonical_name(produto):
    normalized = normalize_text(produto)
    explicit = DESCRIPTION_CANONICAL_OVERRIDES.get(normalized)
    if explicit:
        return explicit

    simplified = simplify_product_text(produto)

    if simplified in {"MACA FUJI", "MACA FUJI KG"}:
        return "Maçã"

    return None


def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()


def extract_product_code(raw_code):
    if not raw_code:
        return None

    match = re.search(r"(\d+)", raw_code)
    return match.group(1) if match else raw_code.strip()


def best_fuzzy_match(produto, product_cache):
    normalized = normalize_text(produto)
    best_match = None
    best_score = 0.0

    for candidate in product_cache["search_space"]:
        score = similarity(normalized, candidate["normalized"])
        if score > best_score:
            best_score = score
            best_match = candidate

    if best_match and best_score >= SIMILARITY_THRESHOLD:
        return best_match, best_score

    return None, best_score


# ==================================================
# EXTRAÇÃO HTML
# ==================================================

def extract_html_data(html_path: Path):
    header = extract_header(html_path)
    chave, _, _, data_emissao, estabelecimento, cnpj = header

    itens = []

    with html_path.open("rb") as f:
        content = f.read()

    try:
        soup = BeautifulSoup(content, "lxml")
    except Exception:
        text = content.decode("cp1252", errors="replace")
        soup = BeautifulSoup(text, "lxml")

    item_index = 0
    for row in soup.select("#tabResult tr"):
        produto = get_text(row.select_one(".txtTit2, .txtTit"))
        if not produto:
            continue

        codigo = get_text(row.select_one(".RCod"))
        if codigo:
            codigo = extract_product_code(codigo)

        qtd = get_text(row.select_one(".Rqtd"))
        if qtd:
            qtd = qtd.replace("Qtde.:", "").strip()

        unit = get_text(row.select_one(".RvlUnit"))
        if unit:
            unit = unit.replace("Vl. Unit.:", "").strip()

        total = get_text(row.select_one(".valor"))
        item_index += 1

        itens.append({
            "id_nota": chave,
            "item_index": item_index,
            "data_emissao": data_emissao,
            "estabelecimento": estabelecimento,
            "cnpj": cnpj,
            "produto": produto,
            "codigo_produto": codigo,
            "quantidade": qtd,
            "valor_unit": unit,
            "valor_total": total,
        })

    return itens


# ==================================================
# DDL
# ==================================================

def create_table(cursor):
    cursor.execute(f"""
        CREATE SCHEMA IF NOT EXISTS {PG_SCHEMA};

        CREATE TABLE IF NOT EXISTS {PG_SCHEMA}.{TABLE_NAME} (
            id_nota TEXT,
            item_index INTEGER,
            data_emissao TEXT,
            estabelecimento TEXT,
            cnpj TEXT,
            produto TEXT,
            codigo_produto TEXT,
            quantidade TEXT,
            valor_unit TEXT,
            valor_total TEXT,
            produto_id INTEGER
        );

        ALTER TABLE {PG_SCHEMA}.{TABLE_NAME}
            ADD COLUMN IF NOT EXISTS item_index INTEGER,
            ADD COLUMN IF NOT EXISTS produto_id INTEGER;
    """)

    cursor.execute(f"""
        WITH deduplicated AS (
            SELECT
                ctid,
                row_number() OVER (
                    PARTITION BY
                        id_nota,
                        item_index
                    ORDER BY ctid
                ) AS duplicate_rank
            FROM {PG_SCHEMA}.{TABLE_NAME}
            WHERE item_index IS NOT NULL
        )
        DELETE FROM {PG_SCHEMA}.{TABLE_NAME} t
        USING deduplicated d
        WHERE t.ctid = d.ctid
          AND d.duplicate_rank > 1;
    """)

    cursor.execute(f"""
        WITH numbered AS (
            SELECT
                ctid,
                row_number() OVER (
                    PARTITION BY id_nota
                    ORDER BY ctid
                ) AS rn
            FROM {PG_SCHEMA}.{TABLE_NAME}
            WHERE item_index IS NULL
        )
        UPDATE {PG_SCHEMA}.{TABLE_NAME} t
        SET item_index = numbered.rn
        FROM numbered
        WHERE t.ctid = numbered.ctid
          AND t.item_index IS NULL;
    """)

    cursor.execute(f"""
        CREATE UNIQUE INDEX IF NOT EXISTS {ITEM_INDEX_NAME}
            ON {PG_SCHEMA}.{TABLE_NAME} (id_nota, item_index);
    """)


def create_header_table(cursor):
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {PG_SCHEMA}.{HEADER_TABLE_NAME} (
            id_nota TEXT PRIMARY KEY,
            numero TEXT,
            serie TEXT,
            data_emissao TEXT,
            estabelecimento TEXT,
            cnpj TEXT
        );
    """)

    cursor.execute(f"""
        WITH deduplicated AS (
            SELECT
                ctid,
                row_number() OVER (
                    PARTITION BY id_nota
                    ORDER BY ctid
                ) AS duplicate_rank
            FROM {PG_SCHEMA}.{HEADER_TABLE_NAME}
        )
        DELETE FROM {PG_SCHEMA}.{HEADER_TABLE_NAME} t
        USING deduplicated d
        WHERE t.ctid = d.ctid
          AND d.duplicate_rank > 1;
    """)

    cursor.execute(f"""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_stg_nf_header_id_nota
            ON {PG_SCHEMA}.{HEADER_TABLE_NAME} (id_nota);
    """)


def create_produto_staging_table(cursor):
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {PG_SCHEMA}.{PRODUTO_STAGING_TABLE} (
            produto_descricao TEXT PRIMARY KEY,
            codigo_produto TEXT,
            primeira_nota_id TEXT,
            primeira_data_emissao TEXT,
            ultimo_nota_id TEXT,
            ultima_data_emissao TEXT,
            estabelecimento TEXT,
            cnpj TEXT,
            sugestao_produto_id INTEGER,
            sugestao_nome_canonico TEXT,
            sugestao_similaridade NUMERIC(5,4),
            quantidade_ocorrencias INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)


# ==================================================
# PRODUTOS
# ==================================================

def nota_already_loaded(cursor, id_nota):
    cursor.execute(
        f"""
        SELECT 1
        FROM {PG_SCHEMA}.{HEADER_TABLE_NAME}
        WHERE id_nota = %s
        UNION
        SELECT 1
        FROM {PG_SCHEMA}.{TABLE_NAME}
        WHERE id_nota = %s
        LIMIT 1
        """,
        (id_nota, id_nota),
    )
    return cursor.fetchone() is not None


def find_existing_note_source(cursor, id_nota):
    cursor.execute(
        f"SELECT 1 FROM {PG_SCHEMA}.{HEADER_TABLE_NAME} WHERE id_nota = %s LIMIT 1",
        (id_nota,),
    )
    in_header = cursor.fetchone() is not None

    cursor.execute(
        f"SELECT 1 FROM {PG_SCHEMA}.{TABLE_NAME} WHERE id_nota = %s LIMIT 1",
        (id_nota,),
    )
    in_items = cursor.fetchone() is not None

    if in_header and in_items:
        return f"{PG_SCHEMA}.{HEADER_TABLE_NAME} e {PG_SCHEMA}.{TABLE_NAME}"
    if in_header:
        return f"{PG_SCHEMA}.{HEADER_TABLE_NAME}"
    if in_items:
        return f"{PG_SCHEMA}.{TABLE_NAME}"
    return None


def load_product_cache(cursor):
    cursor.execute("""
        SELECT d.descricao, p.produto_id, p.nome_canonico
        FROM analytics.dim_produto_descricao d
        JOIN analytics.dim_produto p ON p.produto_id = d.produto_id
    """)
    description_rows = cursor.fetchall()

    cursor.execute("""
        SELECT produto_id, nome_canonico
        FROM analytics.dim_produto
    """)
    product_rows = cursor.fetchall()

    by_description = {}
    by_canonical = {}
    by_simplified_description = {}
    by_simplified_canonical = {}
    search_space = []
    seen_keys = set()

    for descricao, produto_id, nome_canonico in description_rows:
        normalized = normalize_text(descricao)
        simplified = simplify_product_text(descricao)
        by_description[normalized] = {
            "produto_id": produto_id,
            "nome_canonico": nome_canonico,
            "matched_by": "descricao",
            "source_value": descricao,
        }
        if simplified:
            by_simplified_description[simplified] = {
                "produto_id": produto_id,
                "nome_canonico": nome_canonico,
                "matched_by": "descricao_simplificada",
                "source_value": descricao,
            }
        key = ("descricao", normalized, produto_id)
        if key not in seen_keys:
            search_space.append({
                "produto_id": produto_id,
                "nome_canonico": nome_canonico,
                "normalized": normalized,
                "matched_by": "descricao",
                "source_value": descricao,
            })
            seen_keys.add(key)

    for produto_id, nome_canonico in product_rows:
        normalized = normalize_text(nome_canonico)
        simplified = simplify_product_text(nome_canonico)
        by_canonical[normalized] = {
            "produto_id": produto_id,
            "nome_canonico": nome_canonico,
            "matched_by": "canonico",
            "source_value": nome_canonico,
        }
        if simplified:
            by_simplified_canonical[simplified] = {
                "produto_id": produto_id,
                "nome_canonico": nome_canonico,
                "matched_by": "canonico_simplificado",
                "source_value": nome_canonico,
            }
        key = ("canonico", normalized, produto_id)
        if key not in seen_keys:
            search_space.append({
                "produto_id": produto_id,
                "nome_canonico": nome_canonico,
                "normalized": normalized,
                "matched_by": "canonico",
                "source_value": nome_canonico,
            })
            seen_keys.add(key)
        simplified_key = ("canonico_simplificado", simplified, produto_id)
        if simplified and simplified_key not in seen_keys:
            search_space.append({
                "produto_id": produto_id,
                "nome_canonico": nome_canonico,
                "normalized": simplified,
                "matched_by": "canonico_simplificado",
                "source_value": nome_canonico,
            })
            seen_keys.add(simplified_key)

    return {
        "by_description": by_description,
        "by_canonical": by_canonical,
        "by_simplified_description": by_simplified_description,
        "by_simplified_canonical": by_simplified_canonical,
        "search_space": search_space,
    }


def resolve_product(produto, product_cache):
    normalized = normalize_text(produto)
    simplified = simplify_product_text(produto)

    exact_description = product_cache["by_description"].get(normalized)
    if exact_description:
        return exact_description, None, 1.0

    exact_canonical = product_cache["by_canonical"].get(normalized)
    if exact_canonical:
        return exact_canonical, None, 1.0

    preferred_canonical = get_preferred_canonical_name(produto)
    if preferred_canonical:
        preferred_match = product_cache["by_canonical"].get(normalize_text(preferred_canonical))
        if preferred_match:
            return preferred_match, preferred_match, 1.0

    simplified_description = product_cache["by_simplified_description"].get(simplified)
    if simplified_description:
        return simplified_description, simplified_description, 1.0

    simplified_canonical = product_cache["by_simplified_canonical"].get(simplified)
    if simplified_canonical:
        return simplified_canonical, simplified_canonical, 1.0

    fuzzy_match, fuzzy_score = best_fuzzy_match(produto, product_cache)
    if fuzzy_match:
        return fuzzy_match, fuzzy_match, fuzzy_score

    return None, None, fuzzy_score


def insert_unresolved_product(cursor, item, suggestion, suggestion_score):
    suggestion_produto_id = suggestion["produto_id"] if suggestion else None
    suggestion_nome = suggestion["nome_canonico"] if suggestion else None
    suggestion_similarity = round(suggestion_score, 4) if suggestion else None

    cursor.execute(f"""
        INSERT INTO {PG_SCHEMA}.{PRODUTO_STAGING_TABLE} (
            produto_descricao,
            codigo_produto,
            primeira_nota_id,
            primeira_data_emissao,
            ultimo_nota_id,
            ultima_data_emissao,
            estabelecimento,
            cnpj,
            sugestao_produto_id,
            sugestao_nome_canonico,
            sugestao_similaridade
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (produto_descricao) DO UPDATE SET
            codigo_produto = COALESCE(EXCLUDED.codigo_produto, {PG_SCHEMA}.{PRODUTO_STAGING_TABLE}.codigo_produto),
            ultimo_nota_id = EXCLUDED.ultimo_nota_id,
            ultima_data_emissao = EXCLUDED.ultima_data_emissao,
            estabelecimento = EXCLUDED.estabelecimento,
            cnpj = EXCLUDED.cnpj,
            sugestao_produto_id = EXCLUDED.sugestao_produto_id,
            sugestao_nome_canonico = EXCLUDED.sugestao_nome_canonico,
            sugestao_similaridade = EXCLUDED.sugestao_similaridade,
            quantidade_ocorrencias = {PG_SCHEMA}.{PRODUTO_STAGING_TABLE}.quantidade_ocorrencias + 1,
            updated_at = CURRENT_TIMESTAMP;
    """, (
        item["produto"],
        item["codigo_produto"],
        item["id_nota"],
        item["data_emissao"],
        item["id_nota"],
        item["data_emissao"],
        item["estabelecimento"],
        item["cnpj"],
        suggestion_produto_id,
        suggestion_nome,
        suggestion_similarity,
    ))


# ==================================================
# LOAD
# ==================================================

def insert_items(cursor, itens):
    query = f"""
        INSERT INTO {PG_SCHEMA}.{TABLE_NAME} (
            id_nota, item_index, data_emissao, estabelecimento, cnpj,
            produto, codigo_produto, quantidade, valor_unit, valor_total, produto_id
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id_nota, item_index) DO UPDATE SET
            data_emissao = EXCLUDED.data_emissao,
            estabelecimento = EXCLUDED.estabelecimento,
            cnpj = EXCLUDED.cnpj,
            produto = EXCLUDED.produto,
            codigo_produto = EXCLUDED.codigo_produto,
            quantidade = EXCLUDED.quantidade,
            valor_unit = EXCLUDED.valor_unit,
            valor_total = EXCLUDED.valor_total,
            produto_id = EXCLUDED.produto_id;
    """

    rows = [
        (
            item["id_nota"],
            item["item_index"],
            item["data_emissao"],
            item["estabelecimento"],
            item["cnpj"],
            item["produto"],
            item["codigo_produto"],
            item["quantidade"],
            item["valor_unit"],
            item["valor_total"],
            item["produto_id"],
        )
        for item in itens
    ]

    cursor.executemany(query, rows)


def extract_header(html_path):
    with html_path.open("rb") as f:
        content = f.read()

    try:
        soup = BeautifulSoup(content, "lxml")
    except Exception:
        text = content.decode("cp1252", errors="replace")
        soup = BeautifulSoup(text, "lxml")

    chave = get_text(soup.select_one(".chave"))
    if not chave:
        raise ValueError(f"Header chave not found in {html_path}")

    chave = re.sub(r"\s+", "", chave)

    estabelecimento = get_text(soup.select_one("#u20"))

    cnpj_text = soup.find(string=lambda x: x and "CNPJ:" in x)
    cnpj = cnpj_text.split(":", 1)[1].strip() if cnpj_text else None

    info_block = soup.get_text(" ", strip=True)

    numero = None
    serie = None
    data_emissao = None

    numero_match = re.search(r'NÃºmero:\s*(\d+)', info_block)
    serie_match = re.search(r'SÃ©rie:\s*(\d+)', info_block)
    data_match = re.search(r'EmissÃ£o:\s*([\d/\s:]+)', info_block)

    if numero_match:
        numero = numero_match.group(1)

    if serie_match:
        serie = serie_match.group(1)

    if data_match:
        data_emissao = data_match.group(1).strip()

    if not numero or not serie or not data_emissao:
        normalized_info_block = normalize_text(info_block)

        if not numero:
            fallback_numero_match = re.search(r"NUMERO:\s*(\d+)", normalized_info_block)
            if fallback_numero_match:
                numero = fallback_numero_match.group(1)

        if not serie:
            fallback_serie_match = re.search(r"SERIE:\s*(\d+)", normalized_info_block)
            if fallback_serie_match:
                serie = fallback_serie_match.group(1)

        if not data_emissao:
            fallback_data_match = re.search(
                r"EMISSAO:\s*(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2})",
                normalized_info_block,
            )
            if fallback_data_match:
                data_emissao = fallback_data_match.group(1).strip()

    return (
        chave,
        numero,
        serie,
        data_emissao,
        estabelecimento,
        cnpj
    )


def insert_header(cursor, header):
    query = f"""
        INSERT INTO {PG_SCHEMA}.{HEADER_TABLE_NAME} (
            id_nota, numero, serie, data_emissao,
            estabelecimento, cnpj
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (id_nota) DO UPDATE SET
            numero = EXCLUDED.numero,
            serie = EXCLUDED.serie,
            data_emissao = EXCLUDED.data_emissao,
            estabelecimento = EXCLUDED.estabelecimento,
            cnpj = EXCLUDED.cnpj;
    """
    cursor.execute(query, header)


def enrich_items_with_product_resolution(cursor, itens, product_cache):
    resolved_count = 0
    unresolved_count = 0
    fuzzy_count = 0

    for item in itens:
        resolved, suggestion, score = resolve_product(item["produto"], product_cache)
        if resolved:
            item["produto_id"] = resolved["produto_id"]
            resolved_count += 1
            if suggestion and score < 1.0:
                fuzzy_count += 1
            continue

        item["produto_id"] = None
        insert_unresolved_product(cursor, item, suggestion, score)
        unresolved_count += 1

    return resolved_count, unresolved_count, fuzzy_count


# ==================================================
# MAIN
# ==================================================

def main():
    html_files = sorted(DATA_DIR.glob("*.html"))

    if not html_files:
        raise RuntimeError("Nenhum HTML encontrado.")

    validate_pg_conn()
    conn = psycopg2.connect(**PG_CONN)
    conn.autocommit = False
    cursor = conn.cursor()

    create_table(cursor)
    create_header_table(cursor)
    create_produto_staging_table(cursor)
    product_cache = load_product_cache(cursor)

    conn.commit()

    total_items = 0
    total_unresolved = 0

    for html_file in html_files:
        print(f"\nProcessando {html_file.name}")

        header = extract_header(html_file)
        if nota_already_loaded(cursor, header[0]):
            source = find_existing_note_source(cursor, header[0])
            print(f"Nota {header[0]} ja existe em {source}. Pulando arquivo.")
            continue

        if not validate_data_emissao(header, html_file):
            print(f"Ignorando {html_file.name} por falta de data_emissao.")
            continue

        itens = extract_html_data(html_file)

        if not itens:
            print("Nenhum item encontrado.")
            continue

        empty_emissao = [item for item in itens if not item["data_emissao"] or not item["data_emissao"].strip()]
        if empty_emissao:
            print(f"data_emissao vazia em itens para {html_file}. Ignorando arquivo.")
            continue

        resolved_count, unresolved_count, fuzzy_count = enrich_items_with_product_resolution(
            cursor, itens, product_cache
        )

        insert_header(cursor, header)
        insert_items(cursor, itens)

        conn.commit()

        total_items += len(itens)
        total_unresolved += unresolved_count

        print(
            f"{len(itens)} itens processados | "
            f"{resolved_count} com produto resolvido | "
            f"{fuzzy_count} por similaridade | "
            f"{unresolved_count} enviados para {PG_SCHEMA}.{PRODUTO_STAGING_TABLE}"
        )

    cursor.close()
    conn.close()

    print(
        f"\nPipeline HTML finalizado com sucesso. "
        f"Itens processados: {total_items}. "
        f"Pendencias em produtos: {total_unresolved}."
    )


if __name__ == "__main__":
    main()
