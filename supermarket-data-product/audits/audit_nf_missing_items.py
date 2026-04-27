from collections import Counter
from pathlib import Path
import importlib.util
import json
import os
import re

import psycopg2
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_ROOT = BASE_DIR / "data" / "Notas Fiscais" / "2026"
COUNTS_AUDIT_PATH = BASE_DIR / "supermarket-data-product" / "audits" / "audit_nf_item_counts_results.json"
OUTPUT_PATH = BASE_DIR / "supermarket-data-product" / "audits" / "audit_nf_missing_items_results.json"


def load_module(filename, module_name):
    module_path = BASE_DIR / "supermarket-data-product" / "loaders" / filename
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


single_loader = load_module("nf_data_load_html.py", "nf_data_load_html_missing_audit")
split_loader = load_module("nf_data_load_html_split.py", "nf_data_load_html_split_missing_audit")


def normalize_value(value):
    if value is None:
        return None
    return re.sub(r"\s+", " ", str(value)).strip()


def item_signature(item):
    return (
        normalize_value(item.get("produto")),
        normalize_value(item.get("codigo_produto")),
        normalize_value(item.get("quantidade")),
        normalize_value(item.get("valor_unit")),
        normalize_value(item.get("valor_total")),
    )


def load_mismatched_notes():
    data = json.loads(COUNTS_AUDIT_PATH.read_text(encoding="utf-8"))
    return data["mismatches"]


def build_html_note_index():
    index = {}

    for html_path in sorted(DATA_ROOT.glob("*/*.html")):
        if html_path.name.endswith("_header.html") or html_path.name.endswith("_item.html"):
            continue

        try:
            header = single_loader.extract_header(html_path)
            items = single_loader.extract_html_data(html_path)
        except Exception:
            continue

        index.setdefault(header[0], {
            "source_type": "single",
            "paths": [],
            "items": items,
            "data_emissao": header[3],
        })
        index[header[0]]["paths"].append(str(html_path))

    for header_path, item_path in split_loader.list_document_pairs():
        try:
            header = split_loader.extract_header(header_path)
            items = split_loader.extract_items(item_path, header)
        except Exception:
            continue

        index.setdefault(header[0], {
            "source_type": "split",
            "paths": [],
            "items": items,
            "data_emissao": header[3],
        })
        index[header[0]]["paths"].extend([str(header_path), str(item_path)])

    return index


def fetch_db_items(note_ids):
    load_dotenv()
    conn = psycopg2.connect(
        host=os.environ["DB_HOST"],
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASS"],
        port=int(os.environ.get("DB_PORT", "5432")),
    )
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id_nota, item_index, produto, codigo_produto, quantidade, valor_unit, valor_total
                FROM staging.stg_nf_item
                WHERE id_nota = ANY(%s)
                ORDER BY id_nota, item_index
                """,
                (note_ids,),
            )
            rows = cursor.fetchall()
    finally:
        conn.close()

    grouped = {}
    for id_nota, item_index, produto, codigo_produto, quantidade, valor_unit, valor_total in rows:
        grouped.setdefault(id_nota, []).append({
            "item_index": item_index,
            "produto": produto,
            "codigo_produto": codigo_produto,
            "quantidade": quantidade,
            "valor_unit": valor_unit,
            "valor_total": valor_total,
        })

    return grouped


def expand_missing_items(html_items, db_items):
    html_counter = Counter(item_signature(item) for item in html_items)
    db_counter = Counter(item_signature(item) for item in db_items)

    missing = []
    for signature, html_count in html_counter.items():
        db_count = db_counter.get(signature, 0)
        delta = html_count - db_count
        if delta <= 0:
            continue

        produto, codigo_produto, quantidade, valor_unit, valor_total = signature
        missing.append({
            "produto": produto,
            "codigo_produto": codigo_produto,
            "quantidade": quantidade,
            "valor_unit": valor_unit,
            "valor_total": valor_total,
            "missing_count": delta,
            "html_count": html_count,
            "db_count": db_count,
        })

    missing.sort(key=lambda row: (-row["missing_count"], row["produto"] or ""))
    return missing


def create_db_table(results):
    load_dotenv()
    conn = psycopg2.connect(
        host=os.environ["DB_HOST"],
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASS"],
        port=int(os.environ.get("DB_PORT", "5432")),
    )
    try:
        with conn.cursor() as cursor:
            cursor.execute("CREATE SCHEMA IF NOT EXISTS staging")
            cursor.execute("DROP TABLE IF EXISTS staging.stg_nf_item_audit_missing_products")
            cursor.execute("""
                CREATE TABLE staging.stg_nf_item_audit_missing_products (
                    id_nota TEXT,
                    data_emissao TEXT,
                    produto TEXT,
                    codigo_produto TEXT,
                    quantidade TEXT,
                    valor_unit TEXT,
                    valor_total TEXT,
                    missing_count INTEGER,
                    html_count INTEGER,
                    db_count INTEGER,
                    source_paths JSONB,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)

            rows = []
            for note in results:
                for item in note["missing_items"]:
                    rows.append((
                        note["id_nota"],
                        note["data_emissao"],
                        item["produto"],
                        item["codigo_produto"],
                        item["quantidade"],
                        item["valor_unit"],
                        item["valor_total"],
                        item["missing_count"],
                        item["html_count"],
                        item["db_count"],
                        json.dumps(note["source_paths"], ensure_ascii=False),
                    ))

            cursor.executemany("""
                INSERT INTO staging.stg_nf_item_audit_missing_products (
                    id_nota, data_emissao, produto, codigo_produto, quantidade,
                    valor_unit, valor_total, missing_count, html_count, db_count, source_paths
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
            """, rows)
        conn.commit()
    finally:
        conn.close()


def main():
    mismatches = load_mismatched_notes()
    html_index = build_html_note_index()
    note_ids = [row["id_nota"] for row in mismatches]
    db_items_by_note = fetch_db_items(note_ids)

    results = []
    for note in mismatches:
        id_nota = note["id_nota"]
        html_note = html_index.get(id_nota)
        if not html_note:
            continue

        missing_items = expand_missing_items(
            html_note["items"],
            db_items_by_note.get(id_nota, []),
        )

        results.append({
            "id_nota": id_nota,
            "data_emissao": note.get("data_emissao"),
            "html_item_count": note.get("html_item_count"),
            "db_item_count": note.get("db_item_count"),
            "delta_items": note.get("delta_items"),
            "source_paths": note.get("source_paths", []),
            "missing_items": missing_items,
        })

    OUTPUT_PATH.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    create_db_table(results)

    print(f"Notas com análise detalhada: {len(results)}")
    print(f"Relatório salvo em: {OUTPUT_PATH}")
    print("Tabela criada: staging.stg_nf_item_audit_missing_products")

    for note in results[:10]:
        print(f"\n{id_nota if False else note['id_nota']} | faltando {len(note['missing_items'])} tipo(s) de item")
        for item in note["missing_items"][:5]:
            print(
                f"- {item['produto']} | cod={item['codigo_produto']} | "
                f"qtd={item['quantidade']} | missing_count={item['missing_count']}"
            )


if __name__ == "__main__":
    main()
