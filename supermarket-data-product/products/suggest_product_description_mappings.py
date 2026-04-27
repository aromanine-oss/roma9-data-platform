import argparse
import importlib.util
import os
from pathlib import Path
import json

import psycopg2
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[2]
OUTPUT_PATH = BASE_DIR / "supermarket-data-product" / "products" / "suggest_product_description_mappings_results.json"


def load_shared_module():
    module_path = BASE_DIR / "supermarket-data-product" / "loaders" / "nf_data_load_html.py"
    spec = importlib.util.spec_from_file_location("nf_data_load_html_shared", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


shared = load_shared_module()
load_dotenv()


def get_conn():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        port=int(os.getenv("DB_PORT", 5432)),
    )


def fetch_pending_descriptions(cursor, limit):
    cursor.execute(
        f"""
        SELECT
            produto_descricao,
            codigo_produto,
            quantidade_ocorrencias,
            sugestao_produto_id,
            sugestao_nome_canonico,
            sugestao_similaridade
        FROM {shared.PG_SCHEMA}.{shared.PRODUTO_STAGING_TABLE}
        ORDER BY quantidade_ocorrencias DESC, produto_descricao
        LIMIT %s
        """,
        (limit,),
    )
    return cursor.fetchall()


def fetch_catalog(cursor):
    cursor.execute(
        """
        SELECT
            d.descricao,
            p.produto_id,
            p.nome_canonico
        FROM analytics.dim_produto_descricao d
        JOIN analytics.dim_produto p ON p.produto_id = d.produto_id
        """
    )
    description_rows = cursor.fetchall()

    cursor.execute(
        """
        SELECT produto_id, nome_canonico
        FROM analytics.dim_produto
        """
    )
    canonical_rows = cursor.fetchall()

    return description_rows, canonical_rows


def build_search_space(description_rows, canonical_rows):
    exact_descriptions = {}
    simplified_descriptions = {}
    exact_canonicals = {}
    simplified_canonicals = {}
    search_space = []
    seen = set()

    for descricao, produto_id, nome_canonico in description_rows:
        normalized = shared.normalize_text(descricao)
        simplified = shared.simplify_product_text(descricao)
        payload = {
            "produto_id": produto_id,
            "nome_canonico": nome_canonico,
            "source_value": descricao,
            "source_type": "descricao",
        }
        exact_descriptions[normalized] = payload
        if simplified:
            simplified_descriptions[simplified] = payload

        key = ("descricao", normalized, produto_id)
        if key not in seen:
            search_space.append({**payload, "comparison_value": normalized})
            seen.add(key)

        simple_key = ("descricao_simplificada", simplified, produto_id)
        if simplified and simple_key not in seen:
            search_space.append({**payload, "comparison_value": simplified, "source_type": "descricao_simplificada"})
            seen.add(simple_key)

    for produto_id, nome_canonico in canonical_rows:
        normalized = shared.normalize_text(nome_canonico)
        simplified = shared.simplify_product_text(nome_canonico)
        payload = {
            "produto_id": produto_id,
            "nome_canonico": nome_canonico,
            "source_value": nome_canonico,
            "source_type": "canonico",
        }
        exact_canonicals[normalized] = payload
        if simplified:
            simplified_canonicals[simplified] = payload

        key = ("canonico", normalized, produto_id)
        if key not in seen:
            search_space.append({**payload, "comparison_value": normalized})
            seen.add(key)

        simple_key = ("canonico_simplificado", simplified, produto_id)
        if simplified and simple_key not in seen:
            search_space.append({**payload, "comparison_value": simplified, "source_type": "canonico_simplificado"})
            seen.add(simple_key)

    return {
        "exact_descriptions": exact_descriptions,
        "simplified_descriptions": simplified_descriptions,
        "exact_canonicals": exact_canonicals,
        "simplified_canonicals": simplified_canonicals,
        "search_space": search_space,
    }


def find_best_match(produto_descricao, catalog):
    normalized = shared.normalize_text(produto_descricao)
    simplified = shared.simplify_product_text(produto_descricao)

    preferred_canonical = shared.get_preferred_canonical_name(produto_descricao)
    if preferred_canonical:
        preferred = catalog["exact_canonicals"].get(shared.normalize_text(preferred_canonical))
        if preferred:
            return preferred, 1.0, "regra_explicita"

    exact = catalog["exact_descriptions"].get(normalized)
    if exact:
        return exact, 1.0, "descricao_exata"

    exact_canonical = catalog["exact_canonicals"].get(normalized)
    if exact_canonical:
        return exact_canonical, 1.0, "canonico_exato"

    simplified_description = catalog["simplified_descriptions"].get(simplified)
    if simplified and simplified_description:
        return simplified_description, 1.0, "descricao_simplificada"

    simplified_canonical = catalog["simplified_canonicals"].get(simplified)
    if simplified and simplified_canonical:
        return simplified_canonical, 1.0, "canonico_simplificado"

    best = None
    best_score = 0.0
    best_reason = None

    for candidate in catalog["search_space"]:
        score = shared.similarity(normalized, candidate["comparison_value"])
        if simplified:
            score = max(score, shared.similarity(simplified, candidate["comparison_value"]))
        if score > best_score:
            best = candidate
            best_score = score
            best_reason = f"fuzzy_{candidate['source_type']}"

    return best, best_score, best_reason


def classify_suggestion(best, score, reason, staging_hint_name, staging_hint_score):
    if reason in {
        "regra_explicita",
        "descricao_exata",
        "canonico_exato",
        "descricao_simplificada",
        "canonico_simplificado",
    }:
        return "seguro"

    if best and score >= 0.88:
        return "seguro"

    if (
        best
        and staging_hint_name
        and best["nome_canonico"] == staging_hint_name
        and staging_hint_score is not None
        and float(staging_hint_score) >= 0.85
        and score >= 0.75
    ):
        return "seguro"

    if best and score >= 0.70:
        return "revisar"

    return "novo_produto"


def mapping_exists(cursor, descricao):
    cursor.execute(
        "SELECT 1 FROM analytics.dim_produto_descricao WHERE descricao = %s LIMIT 1",
        (descricao,),
    )
    return cursor.fetchone() is not None


def apply_mapping(cursor, descricao, produto_id):
    cursor.execute(
        """
        INSERT INTO analytics.dim_produto_descricao (descricao, produto_id)
        VALUES (%s, %s)
        ON CONFLICT (descricao) DO NOTHING
        """,
        (descricao, produto_id),
    )


def main():
    parser = argparse.ArgumentParser(
        description="Sugere mapeamentos de descrições pendentes para analytics.dim_produto_descricao."
    )
    parser.add_argument("--limit", type=int, default=200, help="Quantidade máxima de pendências a analisar.")
    parser.add_argument(
        "--apply-threshold",
        type=float,
        default=None,
        help="Aplica automaticamente sugestões com score maior ou igual a este valor.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Não aplica nada, apenas exibe sugestões.")
    args = parser.parse_args()

    conn = get_conn()
    cursor = conn.cursor()

    pending_rows = fetch_pending_descriptions(cursor, args.limit)
    description_rows, canonical_rows = fetch_catalog(cursor)
    catalog = build_search_space(description_rows, canonical_rows)

    print(f"Pendências analisadas: {len(pending_rows)}")
    print(f"Descrições já mapeadas: {len(description_rows)}")
    print(f"Produtos canônicos: {len(canonical_rows)}")
    print()

    applied = 0
    triage_counts = {"seguro": 0, "revisar": 0, "novo_produto": 0}
    results = []

    for (
        produto_descricao,
        codigo_produto,
        quantidade_ocorrencias,
        sugestao_produto_id,
        sugestao_nome_canonico,
        sugestao_similaridade,
    ) in pending_rows:
        if mapping_exists(cursor, produto_descricao):
            continue

        best, score, reason = find_best_match(produto_descricao, catalog)
        classification = classify_suggestion(
            best,
            score,
            reason,
            sugestao_nome_canonico,
            sugestao_similaridade,
        )
        triage_counts[classification] += 1

        db_hint = ""
        if sugestao_nome_canonico:
            db_hint = f" | staging_hint={sugestao_nome_canonico} ({sugestao_similaridade})"

        if best:
            print(
                f"[{classification.upper()} {score:.0%}] {produto_descricao} -> {best['nome_canonico']} "
                f"[{reason}] occ={quantidade_ocorrencias} cod={codigo_produto}{db_hint}"
            )
            if (
                args.apply_threshold is not None
                and score >= args.apply_threshold
                and classification == "seguro"
                and not args.dry_run
            ):
                apply_mapping(cursor, produto_descricao, best["produto_id"])
                applied += 1
        else:
            print(
                f"[NOVO_PRODUTO] {produto_descricao} occ={quantidade_ocorrencias} cod={codigo_produto}{db_hint}"
            )

        results.append({
            "produto_descricao": produto_descricao,
            "codigo_produto": codigo_produto,
            "quantidade_ocorrencias": quantidade_ocorrencias,
            "staging_hint_produto_id": sugestao_produto_id,
            "staging_hint_nome_canonico": sugestao_nome_canonico,
            "staging_hint_similaridade": sugestao_similaridade,
            "suggested_produto_id": best["produto_id"] if best else None,
            "suggested_nome_canonico": best["nome_canonico"] if best else None,
            "score": score if best else None,
            "reason": reason,
            "classification": classification,
        })

    if args.apply_threshold is not None and not args.dry_run:
        conn.commit()

    OUTPUT_PATH.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    cursor.execute(f"DROP TABLE IF EXISTS {shared.PG_SCHEMA}.stg_produtos_suggestions")
    cursor.execute(f"""
        CREATE TABLE {shared.PG_SCHEMA}.stg_produtos_suggestions (
            produto_descricao TEXT PRIMARY KEY,
            codigo_produto TEXT,
            quantidade_ocorrencias INTEGER,
            staging_hint_produto_id INTEGER,
            staging_hint_nome_canonico TEXT,
            staging_hint_similaridade NUMERIC(5,4),
            suggested_produto_id INTEGER,
            suggested_nome_canonico TEXT,
            score NUMERIC(5,4),
            reason TEXT,
            classification TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.executemany(
        f"""
        INSERT INTO {shared.PG_SCHEMA}.stg_produtos_suggestions (
            produto_descricao, codigo_produto, quantidade_ocorrencias,
            staging_hint_produto_id, staging_hint_nome_canonico, staging_hint_similaridade,
            suggested_produto_id, suggested_nome_canonico, score, reason, classification
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        [
            (
                row["produto_descricao"],
                row["codigo_produto"],
                row["quantidade_ocorrencias"],
                row["staging_hint_produto_id"],
                row["staging_hint_nome_canonico"],
                row["staging_hint_similaridade"],
                row["suggested_produto_id"],
                row["suggested_nome_canonico"],
                row["score"],
                row["reason"],
                row["classification"],
            )
            for row in results
        ],
    )
    conn.commit()

    print()
    print(f"Seguros: {triage_counts['seguro']}")
    print(f"Revisar: {triage_counts['revisar']}")
    print(f"Novo produto: {triage_counts['novo_produto']}")
    print(f"Relatório salvo em: {OUTPUT_PATH}")
    print(f"Tabela criada: {shared.PG_SCHEMA}.stg_produtos_suggestions")
    if args.apply_threshold is not None:
        if args.dry_run:
            print("Dry run ativado. Nenhuma sugestão foi aplicada.")
        else:
            print(f"Mapeamentos aplicados: {applied}")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    main()
