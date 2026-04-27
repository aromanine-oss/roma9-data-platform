from __future__ import annotations

import argparse
import os
from collections import Counter
from typing import Dict, Iterable, List, Tuple

import psycopg2
from dotenv import load_dotenv

load_dotenv()

CATEGORY_MAP = {
    1: "Frutas e Verduras",
    2: "Carnes e Aves",
    3: "Frios e Laticínios",
    4: "Padaria e Confeitaria",
    5: "Mercearia e Grãos",
    6: "Bebidas não Alcoólicas",
    7: "Bebidas Alcoólicas",
    8: "Doces e Chocolates",
    9: "Congelados e Semi-prontos",
    10: "Limpeza e Higiene",
    11: "Utilidades Domésticas",
    12: "Pets",
}

PATTERNS: List[Tuple[Iterable[str], int]] = [
    (['VINHO', 'VHO', 'VODKA', 'CERVEJA', 'CERV.', 'CERV', 'CHAMPAGNE', 'ESPUMANTE'], 7),
    (['AGUA ', 'AGUA_', 'AGUA.', 'PEPSI', 'COCA COLA', 'FANTA', 'REFRIG', 'SUCO', 'BEB CRYSTAL', 'STARBUCKS', 'CAFE', 'CAPSULA', 'CHÁ', 'CHA', 'BEBIDA DE AVEIA'], 6),
    (['ABOBRINHA', 'CEBOLA', 'CENOURA', 'ALFACE', 'PERA', 'LARANJA', 'MAÇÃ', 'MACA', 'TOMATE', 'VAGEM', 'BANANA', 'CRANBERRY', 'LIMÃO', 'LIMAO', 'MORANGA', 'CHUCHU', 'SOPA', 'CENOURA', 'SALADA'], 1),
    (['BACON', 'PRESUNTO', 'SOBRECOXA', 'COXAO', 'PATO', 'MORTADELA', 'CONTRA FILE', 'COPA FATIADO', 'ATUM', 'PATINHO', 'FILE', 'LOMBO'], 2),
    (['QUEIJO', 'QJ', 'LEITE', 'CREME', 'Iogurte'.upper(), 'REQUEIJÃO', 'RICOTA'], 3),
    (['PÃO', 'PAO', 'BISCOITO', 'BOLO', 'MUFFINS', 'GRISSINI', 'BATATA PALHA', 'SALG.', 'SALG', 'BOMBOM', 'CHOC', 'QUEIJADINHA', 'COOKIE', 'PÃO', 'PÃO', 'PANETONE'], 4),
    (['AÇÚCAR', 'ACUCAR', 'FARINHA', 'MILHO', 'CALDO', 'ESSENCIA', 'CARVAO', 'CASTANHA', 'MACARRÃO', 'TAPIOCA', 'OVO', 'SACHE', 'SACHE', 'SAL', 'ARROZ', 'FEIJÃO', 'FEIJAO', 'TEMPERO', 'MAIONESE', 'MOLHO', 'VINAGRE', 'OEL0', 'ÓLEO', 'OLEO', 'HORTALIÇA'], 5),
    (['REXONA', 'LIMP', 'COND', 'SHAMPOO', 'SH ', 'ESPONJA', 'LIMPOL', 'LIMPA VIDRO', 'MULTIUSO', 'COPOS TERMICOS', 'SACOLA TERMICA', 'FILTO', 'FILTRO', 'PAPEL HIGIÊNICO', 'PAPEL HIGIENICO', 'PAPEL', 'SABÃO', 'AMACIANTE', 'DESINF'], 10),
    (['SACOLA', 'SORVETEIRA', 'MULTIUSO', 'COPOS TERMICOS', 'CALÇA', 'CALCA', 'PORTA PÃO', 'PORTA PAO', 'ORGANIZADOR', 'GAVETA', 'UTENSILIO'], 11),
    (['PEDIGREE', 'RAÇÃO', 'RACAO', 'AREIA', 'ALIMENTO PET', 'PET'], 12),
]

DEFAULT_CATEGORY_ID = 11


def get_conn():
    pg_conn = {
        'host': os.getenv('DB_HOST'),
        'dbname': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASS'),
        'port': int(os.getenv('DB_PORT', 5432)),
    }
    missing = [k for k, v in pg_conn.items() if v is None]
    if missing:
        raise EnvironmentError(f"Missing Postgres env vars: {', '.join(missing)}")
    return psycopg2.connect(**pg_conn)


def classify_product(nome: str) -> int:
    upper = nome.upper()
    for keywords, category_id in PATTERNS:
        if any(keyword in upper for keyword in keywords):
            return category_id
    return DEFAULT_CATEGORY_ID


def load_missing_products(cursor) -> List[Tuple[int, str]]:
    cursor.execute(
        '''
        SELECT produto_id, nome_canonico
        FROM analytics.dim_produto
        WHERE categoria_id IS NULL
        ORDER BY nome_canonico;
        '''
    )
    return cursor.fetchall()


def update_categories(cursor, updates: List[Tuple[int, int]]):
    query = '''
        UPDATE analytics.dim_produto
        SET categoria_id = %s
        WHERE produto_id = %s
    '''
    cursor.executemany(query, [(category_id, produto_id) for produto_id, category_id in updates])


def parse_args():
    parser = argparse.ArgumentParser(
        description='Classifica produtos faltando na dimensão analytics.dim_produto por categoria.'
    )
    parser.add_argument('--dry-run', action='store_true', help='Somente exibir as classificações sem atualizar o banco.')
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    conn = get_conn()
    cursor = conn.cursor()

    missing = load_missing_products(cursor)
    if not missing:
        print('Nenhum produto com categoria nula encontrado.')
        cursor.close()
        conn.close()
        return

    updates: List[Tuple[int, int]] = []
    summary: Counter[int] = Counter()

    print(f'Produtos a classificar: {len(missing)}')
    for produto_id, nome_canonico in missing:
        categoria_id = classify_product(nome_canonico)
        updates.append((produto_id, categoria_id))
        summary[categoria_id] += 1
        print(f'{produto_id:5d} | {categoria_id:2d} {CATEGORY_MAP[categoria_id]:20s} | {nome_canonico}')

    print('\nResumo de categorias atribuídas:')
    for categoria_id, count in summary.most_common():
        print(f'  {categoria_id:2d} {CATEGORY_MAP[categoria_id]:20s}: {count}')

    if args.dry_run:
        print('\nDry run habilitado. Nenhuma alteração foi aplicada.')
    else:
        update_categories(cursor, updates)
        conn.commit()
        print('\nAtualização finalizada com sucesso.')

    cursor.close()
    conn.close()


if __name__ == '__main__':
    main()
