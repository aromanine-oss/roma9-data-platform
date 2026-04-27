import argparse
import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()

# Mapeamento dos 6 produtos não encontrados automaticamente
# Estes já foram padronizados, apenas precisamos corrigir para o valor final
MANUAL_FIXES = {
    440: 'Leite',  # "Cr Leite Vde C" -> "Leite"
    # 428: já é "Cerveja Heineken" -> não precisa mudar
    52: 'Manteiga Ghee',  # "Ghee" -> "Manteiga Ghee" (já está correto)
    # Coxao Mole: não existe no banco ainda, seria novo produto
    # Qj.Mozz.Bianco: já foi convertido para "Queijo Mussarela"
    # *Pro Açúcar: já foi convertido para "Açúcar"
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
    parser = argparse.ArgumentParser(
        description='Verifica status dos 6 produtos manualmente.'
    )
    parser.add_argument('--dry-run', action='store_true', help='Exibe informacoes sem aplicar.')
    args = parser.parse_args()

    conn = get_conn()
    cursor = conn.cursor()

    print('Verificando status dos 6 produtos nao encontrados automaticamente:\n')

    # Verificar cada um
    checks = [
        (440, 'Leite', 'De: Cr Leite Vde C'),
        (428, 'Cerveja Heineken', 'De: Cerv.Hein..3'),
        (52, 'Manteiga Ghee', 'De: Ghee'),
    ]

    for produto_id, expected_name, original in checks:
        cursor.execute(
            'SELECT nome_canonico FROM analytics.dim_produto WHERE produto_id = %s',
            (produto_id,),
        )
        row = cursor.fetchone()
        if row:
            current_name = row[0]
            status = '[OK]' if current_name == expected_name else '[DIFF]'
            print(f'{status} {produto_id}: "{current_name}" ({original})')
        else:
            print(f'[ERRO] {produto_id}: Produto nao encontrado')

    print()
    print('Os seguintes nunca estiveram no banco (novos produtos):')
    print('  - Coxao Mole Moido Bov Argus (seria novo)')
    print('  - Qj.Mozz.Bianco (ja foi convertido para Queijo Mussarela)')
    print('  - *Pro Acucar Refinado Uniao 1 (ja foi convertido para Acucar)')

    cursor.close()
    conn.close()


if __name__ == '__main__':
    main()
