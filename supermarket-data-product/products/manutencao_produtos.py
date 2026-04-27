#!/usr/bin/env python3
"""
Script de manutenção mensal para produtos não mapeados
Executar após carregar novas notas fiscais
"""

import os
from pathlib import Path
import psycopg2
from dotenv import load_dotenv

def main():
    # Carregar configurações
    load_dotenv(dotenv_path=Path('.env'))
    conn = psycopg2.connect(
        host=os.environ['DB_HOST'],
        dbname=os.environ['DB_NAME'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASS'],
        port=int(os.environ.get('DB_PORT', '5432'))
    )

    with conn:
        with conn.cursor() as cur:
            print("=== RELATORIO MENSAL DE PRODUTOS NAO MAPEADOS ===\n")

            # Executar relatório
            cur.execute("SELECT * FROM analytics.relatorio_produtos_nao_mapeados()")
            rows = cur.fetchall()

            if not rows:
                print("Todos os produtos estao mapeados!")
                return

            print(f"Encontrados {len(rows)} produtos não mapeados:")
            print("-" * 80)
            print("<15")
            print("-" * 80)

            total_valor = 0
            for row in rows:
                produto, qtd, valor, primeira, ultima = row
                print("<15")
                total_valor += valor

            print("-" * 80)
            print("<15")
            print("\n=== PROXIMOS PASSOS ===")
            print("1. Analisar os produtos acima")
            print("2. Adicionar novos produtos canônicos em analytics.dim_produto")
            print("3. Mapear descrições em analytics.dim_produto_descricao")
            print("4. Ou atualizar supermarket-data-product/products/DIM_produtos.sql e executar novamente")

if __name__ == "__main__":
    main()
