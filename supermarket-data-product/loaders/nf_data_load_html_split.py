from pathlib import Path
import importlib.util
import re

from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data" / "Notas Fiscais" / "2026" / "Angeloni"


def load_shared_module():
    module_path = Path(__file__).with_name("nf_data_load_html.py")
    spec = importlib.util.spec_from_file_location("nf_data_load_html_shared", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


shared = load_shared_module()


def parse_html(html_path: Path):
    content = html_path.read_bytes()
    try:
        return BeautifulSoup(content, "lxml")
    except Exception:
        text = content.decode("cp1252", errors="replace")
        return BeautifulSoup(text, "lxml")


def normalize_label(text):
    return shared.normalize_text(text).replace(":", "")


def clean_text(text):
    if not text:
        return None
    return re.sub(r"\s+", " ", text).strip()


def extract_label_map(container):
    values = {}
    if not container:
        return values

    for cell in container.select("td"):
        label_node = cell.find("label")
        span_node = cell.find("span")
        if not label_node or not span_node:
            continue
        label = normalize_label(label_node.get_text(" ", strip=True))
        value = clean_text(span_node.get_text(" ", strip=True))
        if label and label not in values:
            values[label] = value

    return values


def extract_header(header_path: Path):
    soup = parse_html(header_path)

    dados_gerais = extract_label_map(soup.select_one("fieldset"))
    dados_nfe = extract_label_map(soup.select_one("#NFe fieldset"))
    emitente = extract_label_map(soup.select("#NFe fieldset")[1] if len(soup.select("#NFe fieldset")) > 1 else None)

    chave = re.sub(r"\s+", "", dados_gerais.get("CHAVE DE ACESSO", ""))
    numero = dados_nfe.get("NUMERO") or dados_gerais.get("NUMERO")
    serie = dados_nfe.get("SERIE")
    data_emissao = dados_nfe.get("DATA DE EMISSAO")
    estabelecimento = emitente.get("NOME / RAZAO SOCIAL")
    cnpj = emitente.get("CNPJ")

    if not chave:
        raise ValueError(f"Header chave not found in {header_path}")

    return (
        chave,
        numero,
        serie,
        data_emissao,
        estabelecimento,
        cnpj,
    )


def extract_items(item_path: Path, header):
    soup = parse_html(item_path)
    chave, _, _, data_emissao, estabelecimento, cnpj = header

    itens = []
    product_section = soup.select_one("#Prod")
    if not product_section:
        return itens

    for toggle in product_section.select("table.toggle"):
        number = shared.get_text(toggle.select_one(".fixo-prod-serv-numero span"))
        produto = clean_text(shared.get_text(toggle.select_one(".fixo-prod-serv-descricao span")))
        quantidade = clean_text(shared.get_text(toggle.select_one(".fixo-prod-serv-qtd span")))
        unidade = clean_text(shared.get_text(toggle.select_one(".fixo-prod-serv-uc span")))
        valor_total = clean_text(shared.get_text(toggle.select_one(".fixo-prod-serv-vb span")))

        detail = toggle.find_next_sibling("table")
        if not detail or "toggable" not in (detail.get("class") or []):
            continue

        detail_values = extract_label_map(detail)
        codigo_produto = detail_values.get("CODIGO DO PRODUTO")
        valor_unit = detail_values.get("VALOR UNITARIO DE COMERCIALIZACAO")

        if not produto or not number:
            continue

        itens.append({
            "id_nota": chave,
            "item_index": int(number),
            "data_emissao": data_emissao,
            "estabelecimento": estabelecimento,
            "cnpj": cnpj,
            "produto": produto,
            "codigo_produto": clean_text(codigo_produto),
            "quantidade": quantidade,
            "valor_unit": valor_unit,
            "valor_total": valor_total,
            "unidade": unidade,
        })

    return itens


def list_document_pairs():
    header_files = sorted(DATA_DIR.glob("*_header.html"))
    pairs = []

    for header_file in header_files:
        base_name = header_file.stem.removesuffix("_header")
        item_file = header_file.with_name(f"{base_name}_item.html")
        if item_file.exists():
            pairs.append((header_file, item_file))

    return pairs


def main():
    pairs = list_document_pairs()
    if not pairs:
        raise RuntimeError("Nenhum par *_header.html / *_item.html encontrado.")

    shared.validate_pg_conn()
    conn = shared.psycopg2.connect(**shared.PG_CONN)
    conn.autocommit = False
    cursor = conn.cursor()

    shared.create_table(cursor)
    shared.create_header_table(cursor)
    shared.create_produto_staging_table(cursor)
    product_cache = shared.load_product_cache(cursor)

    conn.commit()

    total_items = 0
    total_unresolved = 0

    for header_file, item_file in pairs:
        print(f"\nProcessando {header_file.name} + {item_file.name}")

        header = extract_header(header_file)
        if shared.nota_already_loaded(cursor, header[0]):
            source = shared.find_existing_note_source(cursor, header[0])
            print(f"Nota {header[0]} ja existe em {source}. Pulando arquivos.")
            continue

        if not shared.validate_data_emissao(header, header_file):
            print(f"Ignorando {header_file.name} por falta de data_emissao.")
            continue

        itens = extract_items(item_file, header)
        if not itens:
            print("Nenhum item encontrado.")
            continue

        resolved_count, unresolved_count, fuzzy_count = shared.enrich_items_with_product_resolution(
            cursor, itens, product_cache
        )

        shared.insert_header(cursor, header)
        shared.insert_items(cursor, itens)
        conn.commit()

        total_items += len(itens)
        total_unresolved += unresolved_count

        print(
            f"{len(itens)} itens processados | "
            f"{resolved_count} com produto resolvido | "
            f"{fuzzy_count} por similaridade | "
            f"{unresolved_count} enviados para {shared.PG_SCHEMA}.{shared.PRODUTO_STAGING_TABLE}"
        )

    cursor.close()
    conn.close()

    print(
        f"\nPipeline HTML split finalizado com sucesso. "
        f"Itens processados: {total_items}. "
        f"Pendencias em produtos: {total_unresolved}."
    )


if __name__ == "__main__":
    main()
