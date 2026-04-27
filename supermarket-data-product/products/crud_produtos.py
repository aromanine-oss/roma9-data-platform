#!/usr/bin/env python3
"""
CRUD para manutenção de produtos e categorias
Interface interativa para gerenciar analytics.dim_produto e analytics.dim_produto_descricao
"""

import os
from pathlib import Path
import psycopg2
from dotenv import load_dotenv

class ProdutoCRUD:
    def __init__(self):
        load_dotenv(dotenv_path=Path('.env'))
        self.conn = psycopg2.connect(
            host=os.environ['DB_HOST'],
            dbname=os.environ['DB_NAME'],
            user=os.environ['DB_USER'],
            password=os.environ['DB_PASS'],
            port=int(os.environ.get('DB_PORT', '5432'))
        )

    def listar_categorias(self):
        """Lista todas as categorias disponíveis"""
        with self.conn.cursor() as cur:
            cur.execute("SELECT categoria_id, nome_categoria FROM analytics.dim_categoria_produto ORDER BY categoria_id")
            categorias = cur.fetchall()
            print("\n=== CATEGORIAS DISPONIVEIS ===")
            for cat_id, nome in categorias:
                print(f"{cat_id}. {nome}")
            return categorias

    def listar_produtos(self, pagina=1, por_pagina=20):
        """Lista produtos com paginação"""
        offset = (pagina - 1) * por_pagina
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT p.produto_id, p.nome_canonico, c.nome_categoria, c.categoria_id
                FROM analytics.dim_produto p
                JOIN analytics.dim_categoria_produto c ON p.categoria_id = c.categoria_id
                ORDER BY p.produto_id
                LIMIT %s OFFSET %s
            """, (por_pagina, offset))
            produtos = cur.fetchall()

            if not produtos:
                print("Nenhum produto encontrado.")
                return

            print(f"\n=== PRODUTOS (Página {pagina}) ===")
            print("<5")
            print("-" * 70)
            for prod_id, nome, categoria, cat_id in produtos:
                print("<5")

            # Contar total para paginação
            cur.execute("SELECT COUNT(*) FROM analytics.dim_produto")
            total = cur.fetchone()[0]
            total_paginas = (total + por_pagina - 1) // por_pagina
            print(f"\nPágina {pagina} de {total_paginas} (Total: {total} produtos)")

            return produtos

    def buscar_produto(self, termo):
        """Busca produtos por nome"""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT p.produto_id, p.nome_canonico, c.nome_categoria, c.categoria_id
                FROM analytics.dim_produto p
                JOIN analytics.dim_categoria_produto c ON p.categoria_id = c.categoria_id
                WHERE LOWER(p.nome_canonico) LIKE LOWER(%s)
                ORDER BY p.nome_canonico
            """, (f'%{termo}%',))
            produtos = cur.fetchall()

            if not produtos:
                print(f"Nenhum produto encontrado com '{termo}'")
                return

            print(f"\n=== RESULTADOS PARA '{termo}' ===")
            print("<5")
            print("-" * 70)
            for prod_id, nome, categoria, cat_id in produtos:
                print("<5")

            return produtos

    def editar_categoria_produto(self, produto_id, nova_categoria_id):
        """Altera a categoria de um produto"""
        with self.conn.cursor() as cur:
            # Verificar se produto existe
            cur.execute("SELECT nome_canonico FROM analytics.dim_produto WHERE produto_id = %s", (produto_id,))
            produto = cur.fetchone()
            if not produto:
                print(f"Produto ID {produto_id} não encontrado.")
                return False

            # Verificar se categoria existe
            cur.execute("SELECT nome_categoria FROM analytics.dim_categoria_produto WHERE categoria_id = %s", (nova_categoria_id,))
            categoria = cur.fetchone()
            if not categoria:
                print(f"Categoria ID {nova_categoria_id} não encontrada.")
                return False

            # Atualizar
            cur.execute("""
                UPDATE analytics.dim_produto
                SET categoria_id = %s
                WHERE produto_id = %s
            """, (nova_categoria_id, produto_id))

            self.conn.commit()
            print(f"Produto '{produto[0]}' movido para categoria '{categoria[0]}'")
            return True

    def listar_descricoes_produto(self, produto_id):
        """Lista todas as descrições mapeadas para um produto"""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT d.descricao, p.nome_canonico
                FROM analytics.dim_produto_descricao d
                JOIN analytics.dim_produto p ON d.produto_id = p.produto_id
                WHERE d.produto_id = %s
                ORDER BY d.descricao
            """, (produto_id,))
            descricoes = cur.fetchall()

            if not descricoes:
                print(f"Nenhuma descrição encontrada para produto ID {produto_id}")
                return

            produto_nome = descricoes[0][1]
            print(f"\n=== DESCRICOES PARA '{produto_nome}' (ID: {produto_id}) ===")
            for i, (desc,) in enumerate(descricoes, 1):
                print(f"{i}. {desc}")

            return descricoes

    def adicionar_produto(self, nome_canonico, categoria_id):
        """Adiciona novo produto canônico"""
        with self.conn.cursor() as cur:
            # Verificar se categoria existe
            cur.execute("SELECT nome_categoria FROM analytics.dim_categoria_produto WHERE categoria_id = %s", (categoria_id,))
            categoria = cur.fetchone()
            if not categoria:
                print(f"Categoria ID {categoria_id} não encontrada.")
                return False

            # Verificar se produto já existe
            cur.execute("SELECT produto_id FROM analytics.dim_produto WHERE nome_canonico = %s", (nome_canonico,))
            if cur.fetchone():
                print(f"Produto '{nome_canonico}' já existe.")
                return False

            # Inserir
            cur.execute("""
                INSERT INTO analytics.dim_produto (nome_canonico, categoria_id)
                VALUES (%s, %s)
                RETURNING produto_id
            """, (nome_canonico, categoria_id))

            produto_id = cur.fetchone()[0]
            self.conn.commit()
            print(f"Produto '{nome_canonico}' adicionado com ID {produto_id} na categoria '{categoria[0]}'")
            return produto_id

    def adicionar_mapeamento_descricao(self, descricao, produto_id):
        """Adiciona mapeamento de descrição para produto"""
        with self.conn.cursor() as cur:
            # Verificar se produto existe
            cur.execute("SELECT nome_canonico FROM analytics.dim_produto WHERE produto_id = %s", (produto_id,))
            produto = cur.fetchone()
            if not produto:
                print(f"Produto ID {produto_id} não encontrado.")
                return False

            # Verificar se mapeamento já existe
            cur.execute("SELECT produto_id FROM analytics.dim_produto_descricao WHERE descricao = %s", (descricao,))
            if cur.fetchone():
                print(f"Descrição '{descricao}' já está mapeada.")
                return False

            # Inserir
            cur.execute("""
                INSERT INTO analytics.dim_produto_descricao (descricao, produto_id)
                VALUES (%s, %s)
            """, (descricao, produto_id))

            self.conn.commit()
            print(f"Descrição '{descricao}' mapeada para produto '{produto[0]}'")
            return True

def menu_principal():
    crud = ProdutoCRUD()

    while True:
        print("\n" + "="*50)
        print("CRUD DE PRODUTOS - MENU PRINCIPAL")
        print("="*50)
        print("1. Listar categorias")
        print("2. Listar produtos")
        print("3. Buscar produto por nome")
        print("4. Editar categoria de produto")
        print("5. Ver descrições de um produto")
        print("6. Adicionar novo produto")
        print("7. Adicionar mapeamento de descrição")
        print("8. Ver produtos não mapeados")
        print("0. Sair")

        try:
            opcao = input("\nEscolha uma opção: ").strip()

            if opcao == "0":
                print("Saindo...")
                break

            elif opcao == "1":
                crud.listar_categorias()

            elif opcao == "2":
                pagina = input("Página (1): ").strip()
                pagina = int(pagina) if pagina.isdigit() else 1
                crud.listar_produtos(pagina)

            elif opcao == "3":
                termo = input("Buscar por nome: ").strip()
                if termo:
                    crud.buscar_produto(termo)

            elif opcao == "4":
                produto_id = input("ID do produto: ").strip()
                if produto_id.isdigit():
                    crud.listar_categorias()
                    nova_cat = input("Nova categoria ID: ").strip()
                    if nova_cat.isdigit():
                        crud.editar_categoria_produto(int(produto_id), int(nova_cat))

            elif opcao == "5":
                produto_id = input("ID do produto: ").strip()
                if produto_id.isdigit():
                    crud.listar_descricoes_produto(int(produto_id))

            elif opcao == "6":
                nome = input("Nome canônico do produto: ").strip()
                if nome:
                    crud.listar_categorias()
                    cat_id = input("Categoria ID: ").strip()
                    if cat_id.isdigit():
                        crud.adicionar_produto(nome, int(cat_id))

            elif opcao == "7":
                descricao = input("Descrição da nota fiscal: ").strip()
                if descricao:
                    # Listar alguns produtos para escolher
                    produtos = crud.listar_produtos(1, 10)
                    if produtos:
                        prod_id = input("ID do produto canônico: ").strip()
                        if prod_id.isdigit():
                            crud.adicionar_mapeamento_descricao(descricao, int(prod_id))

            elif opcao == "8":
                # Usar a função existente
                with crud.conn.cursor() as cur:
                    cur.execute("SELECT * FROM analytics.relatorio_produtos_nao_mapeados() LIMIT 20")
                    rows = cur.fetchall()
                    if rows:
                        print("\n=== PRODUTOS NAO MAPEADOS ===")
                        print("<20")
                        print("-" * 80)
                        for row in rows:
                            desc, qtd, valor, primeira, ultima = row
                            print("<20")
                    else:
                        print("Todos os produtos estão mapeados!")

            else:
                print("Opção inválida.")

        except KeyboardInterrupt:
            print("\n\nInterrompido pelo usuário. Saindo...")
            break
        except Exception as e:
            print(f"Erro: {e}")

        input("\nPressione Enter para continuar...")

if __name__ == "__main__":
    menu_principal()