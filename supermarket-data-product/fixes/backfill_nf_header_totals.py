from pathlib import Path
import importlib.util


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_ROOT = BASE_DIR / "data" / "Notas Fiscais" / "2026"
LOADER_DIR = BASE_DIR / "supermarket-data-product" / "loaders"


def load_module(filename, module_name):
    module_path = LOADER_DIR / filename
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


single_loader = load_module("nf_data_load_html.py", "nf_data_load_html_backfill")
split_loader = load_module("nf_data_load_html_split.py", "nf_data_load_html_split_backfill")


def collect_single_file_headers():
    for html_path in sorted(DATA_ROOT.rglob("*.html")):
        if html_path.name.endswith("_header.html") or html_path.name.endswith("_item.html"):
            continue

        try:
            header = single_loader.extract_header(html_path)
        except Exception as exc:
            yield "single", html_path, None, exc
            continue

        yield "single", html_path, header, None


def collect_split_headers():
    for header_path in sorted(DATA_ROOT.rglob("*_header.html")):
        item_path = header_path.with_name(
            f"{header_path.stem.removesuffix('_header')}_item.html"
        )
        if not item_path.exists():
            continue

        try:
            header = split_loader.extract_header(header_path)
        except Exception as exc:
            yield "split", header_path, None, exc
            continue

        yield "split", header_path, header, None


def iter_headers():
    yield from collect_single_file_headers()
    yield from collect_split_headers()


def update_header_totals(cursor, header):
    cursor.execute(
        f"""
        UPDATE {single_loader.PG_SCHEMA}.{single_loader.HEADER_TABLE_NAME}
        SET
            vlr_total = %s,
            vlr_desconto = %s,
            vlr_pago = %s
        WHERE id_nota = %s
        """,
        (header[6], header[7], header[8], header[0]),
    )
    return cursor.rowcount


def main():
    single_loader.validate_pg_conn()

    conn = single_loader.psycopg2.connect(**single_loader.PG_CONN)
    conn.autocommit = False

    found = 0
    updated = 0
    not_in_db = 0
    without_values = 0
    parse_errors = []
    seen_notes = set()

    try:
        with conn.cursor() as cursor:
            single_loader.create_header_table(cursor)

            for source_type, html_path, header, error in iter_headers():
                found += 1
                if error:
                    parse_errors.append(f"{source_type}: {html_path} -> {error}")
                    continue

                id_nota = header[0]
                if id_nota in seen_notes:
                    continue
                seen_notes.add(id_nota)

                if header[6] is None and header[7] is None and header[8] is None:
                    without_values += 1
                    continue

                row_count = update_header_totals(cursor, header)
                if row_count:
                    updated += row_count
                else:
                    not_in_db += 1

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    print("Backfill de totais do header finalizado.")
    print(f"Arquivos de nota encontrados: {found}")
    print(f"Notas unicas processadas: {len(seen_notes)}")
    print(f"Notas atualizadas no banco: {updated}")
    print(f"Notas nao encontradas no banco: {not_in_db}")
    print(f"Notas sem valores extraidos: {without_values}")

    if parse_errors:
        print(f"Erros de parse: {len(parse_errors)}")
        for error in parse_errors:
            print(error)


if __name__ == "__main__":
    main()
