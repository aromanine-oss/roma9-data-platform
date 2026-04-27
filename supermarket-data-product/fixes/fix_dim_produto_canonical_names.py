from __future__ import annotations

import argparse
import os
import re
from typing import Iterable

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

SPECIAL_CANONICAL_MAP: list[tuple[re.Pattern, str]] = [
    (re.compile(r'COCA\s*COLA', re.I), 'Refrigerante Coca-Cola'),
    (re.compile(r'PEPSI', re.I), 'Refrigerante Pepsi'),
    (re.compile(r'FANTA', re.I), 'Refrigerante Fanta'),
    (re.compile(r'SCHWEPPES', re.I), 'Água Tônica Schweppes'),
    (re.compile(r'BEB CRYSTAL', re.I), 'Bebida Crystal'),
    (re.compile(r'CAFE\s*MELITTA', re.I), 'Café Melitta'),
    (re.compile(r'QUEIJO\s*MUSSARELA', re.I), 'Queijo Mussarela'),
    (re.compile(r'QUEIJO\s*PARMESA?O', re.I), 'Queijo Parmesão'),
    (re.compile(r'PRESUNTO', re.I), 'Presunto'),
    (re.compile(r'SOBRECOXA', re.I), 'Sobrecoxa de Frango'),
    (re.compile(r'OVO.*BRANCO', re.I), 'Ovo de Galinha Branco'),
    (re.compile(r'OVO.*VERMELHO|CAIPIRA', re.I), 'Ovo de Galinha Vermelho'),
    (re.compile(r'BATATA\s*PALHA', re.I), 'Batata Palha'),
    (re.compile(r'PAO\s*FRANCES|PÃO\s*FRANCÊS|PAO\s*ANG?\s*F?RANCES', re.I), 'Pão Francês'),
    (re.compile(r'PAO\s*INTEGRAL|PÃO\s*INTEGRAL|PAO\s*INTEG', re.I), 'Pão Integral'),
    (re.compile(r'TAPIOCA', re.I), 'Tapioca'),
    (re.compile(r'AGUA\s*MINERAL', re.I), 'Água Mineral'),
    (re.compile(r'AGUA\s*SABOR.*PEDRA', re.I), 'Água da Pedra'),
    (re.compile(r'AGUA\s*S\s*PELLEGRINO', re.I), 'Água Mineral San Pellegrino'),
    (re.compile(r'BEBIDA\s*VEGETAL|BEBIDA\s*DE\s*AVEIA|BEBIDA\s*PROTEICA', re.I), 'Bebida de Aveia'),
    (re.compile(r'AGUA\s*MINERAL\s*AGUA\s*PURA', re.I), 'Água Mineral Água Pura'),
    (re.compile(r'CALCA\s*MASC', re.I), 'Calça Masculina'),
    (re.compile(r'COND\s*ELSEVE', re.I), 'Condicionador Elseve'),
    (re.compile(r'CAFE\s*MELITTA\s*2|CAFE\s*MELITTA\s*REG', re.I), 'Café Melitta'),
    (re.compile(r'VEINHO|VHO\s*ARG|VINHO', re.I), 'Vinho'),
    (re.compile(r'BAT\.LAYS', re.I), 'Batata Lays'),
    (re.compile(r'PICOLE', re.I), 'Picolé'),
    (re.compile(r'MULTIUSO', re.I), 'Multiuso'),
    (re.compile(r'REFRIG\s*CINI\s*GENGIBIRRA', re.I), 'Refrigerante Cini Gengibirra'),
    (re.compile(r'REFRIG\.CINI\s*LA', re.I), 'Refrigerante Cini La'),
]

REMOVE_TOKENS = [
    r'\*PR\*',
    r'\*PRO\*',
    r'PROMOCAO',
    r'PROMO',
    r'PCT',
    r'CT',
    r'CX',
    r'LT',
    r'KG',
    r'G',
    r'ML',
    r'UN',
    r'PET',
    r'CTAMPA',
    r'FAT',
    r'PROMOCAO',
    r'PROMO',
    r'REG',
    r'BRAS',
    r'FR',
    r'R',
    r'P',
    r'DE',
    r'COM',
    r'DO',
    r'DA',
    r'DAS',
    r'DOS',
    r'POR',
]

REPLACEMENTS = {
    'PAO': 'Pão',
    'ACUCAR': 'Açúcar',
    'AGUA': 'Água',
    'CADEIA': 'Cadeia',
    'CAFE': 'Café',
    'CHA': 'Chá',
    'BEBIDA': 'Bebida',
    'REFRIG': 'Refrigerante',
    'ESPUMANTE': 'Espumante',
    'LOMBO': 'Lombo',
    'SUINO': 'Suíno',
    'SOBRECOXA': 'Sobrecoxa',
    'FRANGO': 'Frango',
    'QUEIJO': 'Queijo',
    'PARMESAO': 'Parmesão',
    'MUSSARELA': 'Mussarela',
    'PRESUNTO': 'Presunto',
    'BISCOITO': 'Biscoito',
    'CHOC': 'Choco',
    'TOMATE': 'Tomate',
    'LARANJA': 'Laranja',
    'MORANGA': 'Moranga',
    'CARVAO': 'Carvão',
    'SALADA': 'Salada',
    'AGUA': 'Água',
    'MINERAL': 'Mineral',
    'TONICA': 'Tônica',
    'VINHO': 'Vinho',
    'BOMBOM': 'Bombom',
    'COCA': 'Coca',
    'COLA': 'Cola',
}


def get_conn():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS'),
        port=int(os.getenv('DB_PORT', 5432)),
    )
    return conn


def clean_name(raw: str) -> str:
    text = raw.strip().upper()
    for token in REMOVE_TOKENS:
        text = re.sub(rf'\b{token}\b', '', text)
    text = re.sub(r'\s+', ' ', text).strip()

    for pattern, canonical in SPECIAL_CANONICAL_MAP:
        if pattern.search(text):
            return canonical

    parts = []
    for token in text.split():
        token = REPLACEMENTS.get(token, token.capitalize())
        parts.append(token)
    cleaned = ' '.join(parts)

    cleaned = re.sub(r'\bPromocao\b', '', cleaned, flags=re.I)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned.title()


def load_bad_products(cursor):
    cursor.execute(
        '''
        SELECT p.produto_id, p.nome_canonico
        FROM analytics.dim_produto p
        JOIN analytics.dim_produto_descricao d ON d.produto_id = p.produto_id
        WHERE p.nome_canonico = d.descricao
        ORDER BY p.produto_id
        '''
    )
    return cursor.fetchall()


def update_canonical(cursor, produto_id: int, canonical: str):
    cursor.execute(
        '''
        UPDATE analytics.dim_produto
        SET nome_canonico = %s
        WHERE produto_id = %s
        ''',
        (canonical, produto_id),
    )


def main():
    parser = argparse.ArgumentParser(description='Ajusta nomes canônicos ruins em analytics.dim_produto.')
    parser.add_argument('--dry-run', action='store_true', help='Exibe alterações sem aplicar.')
    args = parser.parse_args()

    conn = get_conn()
    cursor = conn.cursor()
    bad_products = load_bad_products(cursor)

    if not bad_products:
        print('Nenhum produto com nome canônico igual à descrição encontrado.')
        cursor.close()
        conn.close()
        return

    changes = []
    for produto_id, nome in bad_products:
        canonical = clean_name(nome)
        if canonical != nome:
            changes.append((produto_id, nome, canonical))

    if not changes:
        print('Nenhuma alteração sugerida para os nomes canônicos existentes.')
        cursor.close()
        conn.close()
        return

    print('Sugestões de nomes canônicos:')
    for produto_id, original, canonical in changes:
        print(f'{produto_id}: "{original}" -> "{canonical}"')

    if args.dry_run:
        print('\nDry run ativado. Nenhuma alteração foi aplicada.')
    else:
        for produto_id, original, canonical in changes:
            update_canonical(cursor, produto_id, canonical)
        conn.commit()
        print(f'\n{len(changes)} produtos atualizados com novos nomes canônicos.')

    cursor.close()
    conn.close()


if __name__ == '__main__':
    main()
