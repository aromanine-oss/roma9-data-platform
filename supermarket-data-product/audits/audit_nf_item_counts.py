from pathlib import Path
import importlib.util
import json

import psycopg2


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_ROOT = BASE_DIR / "data" / "Notas Fiscais" / "2026"
OUTPUT_PATH = BASE_DIR / "supermarket-data-product" / "audits" / "audit_nf_item_counts_results.json"


def load_module(filename, module_name):
    module_path = BASE_DIR / "supermarket-data-product" / "loaders" / filename
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


single_loader = load_module("nf_data_load_html.py", "nf_data_load_html_audit")
split_loader = load_module("nf_data_load_html_split.py", "nf_data_load_html_split_audit")


def collect_single_file_notes():
    notes = []

    for html_path in sorted(DATA_ROOT.glob("*/*.html")):
        if html_path.name.endswith("_header.html") or html_path.name.endswith("_item.html"):
            continue

        try:
            header = single_loader.extract_header(html_path)
            items = single_loader.extract_html_data(html_path)
        except Exception as exc:
            notes.append({
                "source_type": "single",
                "source_path": str(html_path),
                "error": str(exc),
            })
            continue

        notes.append({
            "source_type": "single",
            "source_path": str(html_path),
            "id_nota": header[0],
            "data_emissao": header[3],
            "html_item_count": len(items),
        })

    return notes


def collect_split_notes():
    notes = []

    for header_path, item_path in split_loader.list_document_pairs():
        try:
            header = split_loader.extract_header(header_path)
            items = split_loader.extract_items(item_path, header)
        except Exception as exc:
            notes.append({
                "source_type": "split",
                "source_path": f"{header_path} | {item_path}",
                "error": str(exc),
            })
            continue

        notes.append({
            "source_type": "split",
            "source_path": f"{header_path} | {item_path}",
            "id_nota": header[0],
            "data_emissao": header[3],
            "html_item_count": len(items),
        })

    return notes


def fetch_db_item_counts():
    conn = psycopg2.connect(**single_loader.PG_CONN)
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id_nota, COUNT(*) AS db_item_count
                FROM staging.stg_nf_item
                GROUP BY id_nota
            """)
            return {id_nota: db_item_count for id_nota, db_item_count in cursor.fetchall()}
    finally:
        conn.close()


def main():
    single_loader.validate_pg_conn()

    html_notes = collect_single_file_notes() + collect_split_notes()
    db_counts = fetch_db_item_counts()

    mismatches = []
    parse_errors = []
    unique_notes = {}

    for note in html_notes:
        if "error" in note:
            parse_errors.append(note)
            continue

        existing = unique_notes.get(note["id_nota"])
        if not existing:
            unique_notes[note["id_nota"]] = {
                **note,
                "source_paths": [note["source_path"]],
            }
            continue

        existing["source_paths"].append(note["source_path"])

        if existing["html_item_count"] != note["html_item_count"]:
            raise ValueError(
                f"Contagem divergente para a mesma nota {note['id_nota']}: "
                f"{existing['html_item_count']} vs {note['html_item_count']}"
            )

    for note in unique_notes.values():
        db_item_count = db_counts.get(note["id_nota"])
        result = {
            **note,
            "db_item_count": db_item_count,
            "delta_items": None if db_item_count is None else note["html_item_count"] - db_item_count,
        }

        if db_item_count is None or db_item_count != note["html_item_count"]:
            mismatches.append(result)

    summary = {
        "total_html_notes": len(unique_notes),
        "total_parse_errors": len(parse_errors),
        "total_mismatches": len(mismatches),
        "mismatches": mismatches,
        "parse_errors": parse_errors,
    }

    OUTPUT_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Notas analisadas: {summary['total_html_notes']}")
    print(f"Erros de parsing: {summary['total_parse_errors']}")
    print(f"Inconsistências encontradas: {summary['total_mismatches']}")
    print(f"Relatório salvo em: {OUTPUT_PATH}")

    if mismatches:
        print("\nPrimeiras inconsistências:")
        for row in mismatches[:20]:
            print(
                f"- {row['id_nota']} | HTML={row['html_item_count']} | "
                f"DB={row['db_item_count']} | origem={row['source_type']}"
            )


if __name__ == "__main__":
    main()
