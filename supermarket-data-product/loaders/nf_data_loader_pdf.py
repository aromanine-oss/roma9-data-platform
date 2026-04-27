from pathlib import Path
import pdfplumber
import psycopg2
import re
import os
from dotenv import load_dotenv

load_dotenv()

# ==================================================
# CONFIG
# ==================================================

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data" / "Notas Fiscais" / "2026" / "mar"

PG_CONN = {
    "host": os.getenv("DB_HOST"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASS"),
    "port": int(os.getenv("DB_PORT", 5432)),
}

PG_SCHEMA = "staging"
TABLE_NAME = "stg_nf_item"

# ==================================================
# EXTRAÇÃO
# ==================================================

def extract_text(pdf_path: Path) -> str:
    with pdfplumber.open(pdf_path) as pdf:
        return "\n".join([p.extract_text() or "" for p in pdf.pages])


def extract_chave(texto: str):
    match = re.search(r'Chave de acesso:\s*([\d\s]+)', texto)
    return match.group(1).replace(" ", "") if match else None


def extract_data_emissao(texto: str):
    match = re.search(r'Emissão:\s*([\d/:\s-]+)', texto)
    return match.group(1).strip() if match else None


def extract_estabelecimento(texto: str):
    linhas = texto.split("\n")
    nome = linhas[0] if linhas else None

    cnpj_match = re.search(r'CNPJ:\s*([\d./-]+)', texto)
    cnpj = cnpj_match.group(1) if cnpj_match else None

    return nome, cnpj


def extract_itens(texto: str):
    linhas = texto.split("\n")

    itens = []
    item_atual = {}

    for i, linha in enumerate(linhas):
        linha = linha.strip()

        # início do item
        if "(Código:" in linha:
            try:
                desc = linha.split("(Código:")[0].strip()
                cod = re.search(r'Código:\s*(\w+)', linha).group(1)

                item_atual = {
                    "desc": desc,
                    "cod": cod
                }
            except:
                continue

        # valor total (linha seguinte)
        elif linha.replace(",", "").replace(".", "").isdigit():
            if item_atual and "total" not in item_atual:
                item_atual["total"] = linha

        # quantidade + unit
        elif "Qtde.:" in linha:
            try:
                qtd = re.search(r'Qtde\.:\s*([\d,]+)', linha).group(1)
                unit = re.search(r'Vl\. Unit\.:\s*([\d,]+)', linha).group(1)

                item_atual["qtd"] = qtd
                item_atual["unit"] = unit

                # item completo → salva
                itens.append((
                    item_atual.get("desc"),
                    item_atual.get("cod"),
                    item_atual.get("qtd"),
                    item_atual.get("unit"),
                    item_atual.get("total"),
                ))

                item_atual = {}

            except:
                continue

    return itens

# ==================================================
# TRANSFORMAÇÃO
# ==================================================

def transform_items(texto: str):
    id_nota = extract_chave(texto)
    data_emissao = extract_data_emissao(texto)
    estabelecimento, cnpj = extract_estabelecimento(texto)

    itens_raw = extract_itens(texto)

    for desc, cod, qtd, unit, total in itens_raw:
        try:
            yield (
                id_nota,
                data_emissao,
                estabelecimento,
                cnpj,
                desc.strip(),
                cod,
                qtd.strip(),
                unit.strip(),
                total.strip()
            )
        except:
            continue


# ==================================================
# DDL
# ==================================================

def create_table(cursor):
    cursor.execute(f"""
        CREATE SCHEMA IF NOT EXISTS {PG_SCHEMA};

        CREATE TABLE IF NOT EXISTS {PG_SCHEMA}.{TABLE_NAME} (
            id_nota TEXT,
            data_emissao TEXT,
            estabelecimento TEXT,
            cnpj TEXT,
            produto TEXT,
            codigo_produto TEXT,
            quantidade TEXT,
            valor_unit TEXT,
            valor_total TEXT
        );
    """)


# ==================================================
# LOAD
# ==================================================

def insert_items(cursor, itens):
    query = f"""
        INSERT INTO {PG_SCHEMA}.{TABLE_NAME} (
            id_nota, data_emissao, estabelecimento, cnpj,
            produto, codigo_produto, quantidade,
            valor_unit, valor_total
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
    """

    cursor.executemany(query, list(itens))


# ==================================================
# MAIN
# ==================================================

def main():
    pdf_files = sorted(DATA_DIR.glob("*.pdf"))

    if not pdf_files:
        raise RuntimeError("Nenhum PDF encontrado no diretório de dados: " + str(DATA_DIR))

    conn = psycopg2.connect(**PG_CONN)
    conn.autocommit = False
    cursor = conn.cursor()

    create_table(cursor)
    conn.commit()

    for pdf_file in pdf_files:
        print(f"\n📥 Processando {pdf_file.name}")

        texto = extract_text(pdf_file)
        itens = list(transform_items(texto))

        if not itens:
            print("⚠️ Nenhum item encontrado.")
            print("Texto extraído:" + texto[:500] + "...")
            continue

        insert_items(cursor, itens)
        conn.commit()

        print(f"✅ {len(itens)} itens inseridos")

    cursor.close()
    conn.close()

    print("\n🎉 Staging carregado com sucesso.")
    

if __name__ == "__main__":
    main()