import argparse
import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()

# DE PARA mapping - apenas os que mudaram
MAPPING = {
    'Grissini Ita A': 'Biscoito Grissini',
    'Cr Leite Vde C': 'Leite',
    'Cerv.Hein..3': 'Cerveja Heineken',
    'Ghee': 'Manteiga Ghee',
    'Coxao Mole Moido Bov Argus': 'Coxão Mole',
    'Pera Willians': 'Pera Williams',
    'Qj.Mozz.Bianco': 'Queijo Mussarela',
    'Vho U Undurraga Cab.': 'Vinho Undurraga',
    'Bebida Crystal': 'Água Saborizada Crystal',
    'Água Sab Água Pedra F Verm Cg 350M': 'Água Saborizada Água Pedra',
    '*Pro Açúcar Refinado Uniao 1': 'Açúcar',
    'Refrigerante Cini La': 'Refrigerante Cini',
    'Choco Ao Leite 2X100G': 'Chocolate Ao Leite',
    'Cenoura Crfo': 'Cenoura',
    'Cerveja Corona Extra 350': 'Cerveja Corona',
    'Posta Vermelha Bov Argus (': 'Posta Vermelha Bovina',
    'Cerv.Coronita': 'Cerveja Corona',
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


def main():
    parser = argparse.ArgumentParser(description='Aplica mapeamento DE PARA de nomes canônicos.')
    parser.add_argument('--dry-run', action='store_true', help='Exibe alterações sem aplicar.')
    args = parser.parse_args()

    conn = get_conn()
    cursor = conn.cursor()

    print(f'Total de mapeamentos: {len(MAPPING)}')
    print()

    applied = 0
    not_found = []

    for old_name, new_name in MAPPING.items():
        cursor.execute(
            'SELECT produto_id FROM analytics.dim_produto WHERE nome_canonico = %s',
            (old_name,),
        )
        row = cursor.fetchone()
        if row:
            produto_id = row[0]
            print(f'{produto_id}: "{old_name}" -> "{new_name}"')
            if not args.dry_run:
                cursor.execute(
                    'UPDATE analytics.dim_produto SET nome_canonico = %s WHERE produto_id = %s',
                    (new_name, produto_id),
                )
            applied += 1
        else:
            not_found.append(old_name)

    if not_found:
        print()
        print(f'Produtos não encontrados ({len(not_found)}):')
        for name in not_found:
            print(f'  - {name}')

    if args.dry_run:
        print()
        print('Dry run ativado. Nenhuma alteração foi aplicada.')
    else:
        conn.commit()
        print()
        print(f'[OK] {applied} produtos atualizados com sucesso.')

    cursor.close()
    conn.close()


if __name__ == '__main__':
    main()
