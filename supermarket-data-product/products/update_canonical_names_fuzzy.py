import argparse
import os
from difflib import SequenceMatcher

import psycopg2
from dotenv import load_dotenv

load_dotenv()

# DE PARA mapping original (como você forneceu)
ORIGINAL_MAPPING = {
    'Vinho Tinto Português': 'Vinho Tinto Português',
    'Limpol Gel Concent V': 'Limpol Gel Concent V',
    'Bebida de Aveia': 'Bebida de Aveia',
    'Vinho Cremashi': 'Vinho Cremashi',
    'Grissini Ita A': 'Biscoito Grissini',
    'Cr Leite Vde C': 'Leite',
    'Cerv.Hein..3': 'Cerveja Heineken',
    'Ghee': 'Manteiga Ghee',
    'Cerveja Caracu': 'Cerveja Caracu',
    'Biscoito Salgado': 'Biscoito Salgado',
    'Coxao Mole Moido Bov Argus': 'Coxão Mole',
    'Pera Willians': 'Pera Williams',
    'Bombom Lacta Favoritos': 'Bombom Lacta Favoritos',
    'Mortadela Ceratti': 'Mortadela Ceratti',
    'Barra de Chocolate Branco c/ Pistache': 'Barra de Chocolate Branco c/ Pistache',
    'Queijo Mussarela': 'Queijo Mussarela',
    'Limpa Sanitário Pato Marine': 'Limpa Sanitário Pato Marine',
    'Sacola Termica 10Kg': 'Sacola Termica 10Kg',
    'Vho U Undurraga Cab.': 'Vinho Undurraga',
    'Manga Palmer': 'Manga Palmer',
    'Qj.Mozz.Bianco': 'Queijo Mussarela',
    'Essencia Dr Oetker Baunilha 30Ml': 'Essencia Dr Oetker Baunilha 30Ml',
    'Pão Charlotte Vollkorn Brot 450G': 'Pão Charlotte Vollkorn Brot 450G',
    'Cranberry': 'Cranberry',
    'Cenoura': 'Cenoura',
    'Refrigerante Fanta': 'Refrigerante Fanta',
    'Tomate Tomini 800G': 'Tomate Tomini 800G',
    'Nuggets de Frango Sadia': 'Nuggets de Frango Sadia',
    'Bebida Crystal': 'Água Saborizada Crystal',
    'Leite Tirol Integral': 'Leite Tirol Integral',
    'Água Sab Água Pedra F Verm Cg 350M': 'Água Saborizada Água Pedra',
    'Berinjela': 'Berinjela',
    'Abobrinha': 'Abobrinha',
    'Bramicar Hct 40 12.5Mg 30Cpr': 'Bramicar',
    'Amaciante Ypê L\'Occitane': 'Amaciante Ypê L\'Occitane',
    'Presunto': 'Presunto',
    'Cerveja Antarctica Orig C12X350Ml Eco': 'Cerveja Antarctica Orig C12X350Ml Eco',
    'Biscoito Polvilho': 'Biscoito Polvilho',
    'Ricota': 'Ricota',
    'Mix Sopa Verde': 'Mix Sopa Verde',
    'Cebola': 'Cebola',
    'Bombom Bacio': 'Bombom Bacio',
    'Bacon Tablete Pamplo': 'Bacon Tablete Pamplo',
    'Bebida de Castanha': 'Bebida de Castanha',
    'Bolo de Páscoa com Gotas': 'Bolo de Páscoa com Gotas',
    'Posta Branca Bov Argus (Ped': 'Posta Branca Bov Argus (Ped',
    'Moranga Cabotiá': 'Moranga Cabotiá',
    'Capsula Nescafe Braz': 'Capsula Nescafe Braz',
    'Milho Pipoca Yoki': 'Milho Pipoca Yoki',
    'Sobrecoxa de Frango': 'Sobrecoxa de Frango',
    'Maionese Maille': 'Maionese Maille',
    '*Pro Açúcar Refinado Uniao 1': 'Açúcar',
    'Condicionador Elseve': 'Condicionador Elseve',
    'Refrigerante Cini La': 'Refrigerante Cini',
    'Bombom Lacta Sonho Valsa 20G': 'Bombom Lacta Sonho Valsa 20G',
    'Choco Nestle Lollo Br 28G': 'Choco Nestle Lollo Br 28G',
    'Contra File Bov Friboi Porc': 'Contra File Bov Friboi Porc',
    'Embutido de Pernil': 'Embutido de Pernil',
    'Vodka Hambre 9': 'Vodka Hambre 9',
    'Cerveja Budweiser': 'Cerveja Budweiser',
    'Macarrão': 'Macarrão',
    'Aveia em Flocos': 'Aveia em Flocos',
    'Farinha Mandioca Tupa 1Kg': 'Farinha Mandioca Tupa 1Kg',
    'Bicarbonato de Sódio': 'Bicarbonato de Sódio',
    'Freddo Ruby Di Bosco': 'Freddo Ruby Di Bosco',
    'Queijo Coalho Buf': 'Queijo Coalho Buf',
    'Multiuso': 'Multiuso',
    'Organizador de Geladeira': 'Organizador de Geladeira',
    'Preparado Easy Drinks Frutas Vermel 1': 'Preparado Easy Drinks',
    'Feijão Branco': 'Feijão Branco',
    'Laranja Bahia': 'Laranja Bahia',
    'Queijadinha Members': 'Queijadinha Members',
    'Choco Ao Leite 2X100G': 'Chocolate Ao Leite',
    'Cenoura Crfo': 'Cenoura',
    'Maca Verde Imp': 'Maca Verde Imp',
    'Cerveja Blue Moon': 'Cerveja Blue Moon',
    'Maçã Pink Lady': 'Maçã Pink Lady',
    'Refrigerante Pepsi': 'Refrigerante Pepsi',
    'Chuchu': 'Chuchu',
    'Bolo de Páscoa com Frutas': 'Bolo de Páscoa com Frutas',
    'Grão de Bico': 'Grão de Bico',
    'Cerveja Corona Extra 350': 'Cerveja Corona',
    'Pão Broa Charlotte Centeio 400G': 'Pão Broa Charlotte Centeio 400G',
    'Salg.Pingo Dou': 'Salg.Pingo Dou',
    'Des Rexona Aero Fem Sem Perfume 90Gr': 'Des Rexona Aero Fem Sem Perfume 90Gr',
    'Pera Williams': 'Pera Williams',
    'Bacon': 'Bacon',
    'Vinho Alto Los Romeros': 'Vinho Alto Los Romeros',
    'Água Mineral': 'Água Mineral',
    'Peito de Frango': 'Peito de Frango',
    'Salsicha Seara': 'Salsicha Seara',
    'Quirera de Arroz': 'Quirera de Arroz',
    'Sorveteira Ice M10Bl': 'Sorveteira Ice M10Bl',
    'Filtro Papel Gde 103': 'Filtro Papel Gde 103',
    'Feijão Fradinho': 'Feijão Fradinho',
    'Pão de Batata': 'Pão de Batata',
    'Maca Gransmith Verde': 'Maca Gransmith Verde',
    'Bebida Proteica': 'Bebida Proteica',
    'Oleo Rep Neutrox Nutre Oleos 45Ml': 'Oleo Rep Neutrox Nutre Oleos 45Ml',
    'Laranja Pera K': 'Laranja Pera K',
    'Cebolinha Verde (A)': 'Cebolinha Verde (A)',
    '*Pr* Bisc Gullon Mega Duo Choco': '*Pr* Bisc Gullon Mega Duo Choco',
    'Limpa Vidro Sq 500Ml': 'Limpa Vidro Sq 500Ml',
    'Chocolate Milka': 'Chocolate Milka',
    'Refrigerante H2OH Limoneto': 'Refrigerante H2OH Limoneto',
    'Lasanha Sadia Calabresa': 'Lasanha Sadia Calabresa',
    'Pedigree Tasty': 'Pedigree Tasty',
    'Refrigerante Coca-Cola': 'Refrigerante Coca-Cola',
    'Vinho Undurraga': 'Vinho Undurraga',
    'Iogurte': 'Iogurte',
    'Água Sabor Crystal L': 'Água Sabor Crystal L',
    'Cerveja Heineken 269Ml': 'Cerveja Heineken 269Ml',
    'Banana Prata': 'Banana Prata',
    'Cerveja Antarctica': 'Cerveja Antarctica',
    'Maionese Hellmanns': 'Maionese Hellmanns',
    'Cerveja Budweiser 350Ml': 'Cerveja Budweiser 350Ml',
    'Qj Proc Cheddar Sand': 'Qj Proc Cheddar Sand',
    'Vinho Branco Chileno': 'Vinho Branco Chileno',
    'Tomate Cereja': 'Tomate Cereja',
    'Café Melitta': 'Café Melitta',
    'Tangerina': 'Tangerina',
    'Posta Vermelha Bov Argus (': 'Posta Vermelha Bovina',
    'Ovo de Chocolate Amargo': 'Ovo de Chocolate Amargo',
    'Salada Ita Str': 'Salada Ita Str',
    'Batata Palha': 'Batata Palha',
    'Água Tônica Schweppes': 'Água Tônica Schweppes',
    'Cebola Crfo': 'Cebola Crfo',
    'Açúcar União': 'Açúcar União',
    'Leite UHT Integral': 'Leite UHT Integral',
    'Molho de Tomate': 'Molho de Tomate',
    'Pão Integral': 'Pão Integral',
    'Tomate Italiano': 'Tomate Italiano',
    'Maca Golden Importada': 'Maca Golden Importada',
    'Lasanha Sadia 4 Queijos': 'Lasanha Sadia 4 Queijos',
    'Água Sab Água Pedra Abahor Cg 350M': 'Água Sab Água Pedra Abahor Cg 350M',
    'Qj.Burrata B.D': 'Qj.Burrata B.D',
    'Salsicha Sadia Hot Dog': 'Salsicha Sadia Hot Dog',
    'Ag Coco Campo Largo': 'Ag Coco Campo Largo',
    'Uva Verde': 'Uva Verde',
    'Nuggets Legume': 'Nuggets Legume',
    'Lentilha Canada': 'Lentilha Canada',
    'Mix Salada': 'Mix Salada',
    'Barra de Chocolate ao Leite': 'Barra de Chocolate ao Leite',
    'Vinho': 'Vinho',
    'Lasanha Sadia Bolonhesa': 'Lasanha Sadia Bolonhesa',
    'Pato Tablete Marine': 'Pato Tablete Marine',
    'Cerveja Bodebrown': 'Cerveja Bodebrown',
    'Filé Mignon Suíno': 'Filé Mignon Suíno',
    'Pão Francês': 'Pão Francês',
    'Creme de Leite UHT': 'Creme de Leite UHT',
    'Cerveja Corona': 'Cerveja Corona',
    'Grissini Ita.': 'Grissini Ita.',
    'Tomate': 'Tomate',
    'Esponja': 'Esponja',
    'Cerveja Heineken': 'Cerveja Heineken',
    'Batata Salsa': 'Batata Salsa',
    'Atum Sólido': 'Atum Sólido',
    'Muffins Sortidos Mem': 'Muffins Sortidos Mem',
    'Ovos Ares Bco.': 'Ovos Ares Bco.',
    'Pão Alho Trad 400G S': 'Pão Alho Trad 400G S',
    'Starbucks Espresso': 'Starbucks Espresso',
    'Requeijão': 'Requeijão',
    'Café Arara': 'Café Arara',
    'Preparado Easy Drinks Maracuja 100G': 'Preparado Easy Drinks Maracuja 100G',
    'Pato Germinex Marine': 'Pato Germinex Marine',
    'Castanha Caju': 'Castanha Caju',
    'Ovo de Galinha Branco': 'Ovo de Galinha Branco',
    'Queijo Prato': 'Queijo Prato',
    'Milho em Lata Knorr': 'Milho em Lata Knorr',
    'Macarrao Nissin Inst T Monica Tomate': 'Macarrao Nissin Inst T Monica Tomate',
    'Carvão Aguia 4': 'Carvão Aguia 4',
    'Tâmaras com Chocolate': 'Tâmaras com Chocolate',
    'Refrigerante Sprite': 'Refrigerante Sprite',
    'Água de Coco': 'Água de Coco',
    'Cebola Flocos (Tempero)': 'Cebola Flocos (Tempero)',
    'Picolé': 'Picolé',
    'Sabão em Pó': 'Sabão em Pó',
    'Cj Copos Termicos Ig': 'Cj Copos Termicos Ig',
    'Papel Higiênico': 'Papel Higiênico',
    'Chá Leão': 'Chá Leão',
    'Vagem Sem Fio': 'Vagem Sem Fio',
    'Alho-poró': 'Alho-poró',
    'Porta Pão': 'Porta Pão',
    'Copa Fatiado 80G Hac': 'Copa Fatiado 80G Hac',
    'Refrigerante Cini Gengibirra': 'Refrigerante Cini Gengibirra',
    'Freddo Pistacchio 50': 'Freddo Pistacchio 50',
    'Caldo Knorr Zero Sal Galinha 48G': 'Caldo Knorr Zero Sal Galinha 48G',
    'Bombom Nestlé': 'Bombom Nestlé',
    'Cebolinha': 'Cebolinha',
    'Refrigerante Cristal Limao 500Ml': 'Refrigerante Cristal Limao 500Ml',
    'Ovo de Galinha Vermelho': 'Ovo de Galinha Vermelho',
    'Lombo Suíno Seara': 'Lombo Suíno Seara',
    'Óleo de Canola': 'Óleo de Canola',
    'Vinagre de Álcool': 'Vinagre de Álcool',
    'Sh Aussie Smooth 180Ml': 'Sh Aussie Smooth 180Ml',
    'Tapioca': 'Tapioca',
    'Alface': 'Alface',
    'Sacola': 'Sacola',
    'Bombom Sonho de Valsa': 'Bombom Sonho de Valsa',
    'Areia para Gatos': 'Areia para Gatos',
    'Salsa em Flocos': 'Salsa em Flocos',
    'Salada Mix Ver': 'Salada Mix Ver',
    'Queijo Coalho': 'Queijo Coalho',
    'Batata Lays': 'Batata Lays',
    'Calça Masculina': 'Calça Masculina',
    'Patinho Moído Bovino': 'Patinho Moído Bovino',
    'Limão com Ervas': 'Limão com Ervas',
    'Limao Thaiti K': 'Limao Thaiti K',
    'Maca Kanzi Imp': 'Maca Kanzi Imp',
    'Batata Monalisa Crfo': 'Batata Monalisa Crfo',
    'Maionese Heinz': 'Maionese Heinz',
    'Big Mentos Tutti Frutti': 'Big Mentos Tutti Frutti',
    'Abacate / Avocado': 'Abacate / Avocado',
    'Salada Strap B': 'Salada Strap B',
    'Molho Ajinomoto': 'Molho Ajinomoto',
    'Mini Sal': 'Mini Sal',
    'Butter Cookies': 'Butter Cookies',
    'Suco': 'Suco',
    'Salsicha Olho Bockwu': 'Salsicha Olho Bockwu',
    'Lombo Suíno Seara (Pedaco)': 'Lombo Suíno Seara (Pedaco)',
    'Batata a Granel': 'Batata a Granel',
    'Azeitona': 'Azeitona',
    'Queijo Parmesão': 'Queijo Parmesão',
    'Cerv.Coronita': 'Cerveja Corona',
    'Cebola Roxa': 'Cebola Roxa',
}

# Apenas os que mudaram
CHANGES_ONLY = {k: v for k, v in ORIGINAL_MAPPING.items() if k != v}


def get_conn():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS'),
        port=int(os.getenv('DB_PORT', 5432)),
    )
    return conn


def similarity(a, b):
    """Calcula similaridade entre duas strings."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def find_closest_match(current_names, target_name, threshold=0.7):
    """Encontra o nome mais próximo no banco de dados."""
    best_match = None
    best_score = threshold
    for name in current_names:
        score = similarity(name, target_name)
        if score > best_score:
            best_score = score
            best_match = name
    return best_match, best_score


def main():
    parser = argparse.ArgumentParser(description='Aplica mapeamento DE PARA com busca fuzzy.')
    parser.add_argument('--dry-run', action='store_true', help='Exibe alterações sem aplicar.')
    args = parser.parse_args()

    conn = get_conn()
    cursor = conn.cursor()

    # Buscar todos os nomes atuais
    cursor.execute('SELECT nome_canonico FROM analytics.dim_produto')
    current_names = {row[0] for row in cursor.fetchall()}

    print(f'Total de mapeamentos com mudancas: {len(CHANGES_ONLY)}')
    print(f'Total de produtos no banco: {len(current_names)}')
    print()

    applied = 0
    not_found = []
    updates = []

    for old_name, new_name in CHANGES_ONLY.items():
        # Primeiro, tenta encontro exato
        if old_name in current_names:
            cursor.execute(
                'SELECT produto_id FROM analytics.dim_produto WHERE nome_canonico = %s',
                (old_name,),
            )
            row = cursor.fetchone()
            if row:
                produto_id = row[0]
                print(f'{produto_id}: "{old_name}" -> "{new_name}" [EXATO]')
                updates.append((new_name, produto_id))
                applied += 1
        else:
            # Tenta busca fuzzy
            match, score = find_closest_match(current_names, old_name, threshold=0.7)
            if match:
                cursor.execute(
                    'SELECT produto_id FROM analytics.dim_produto WHERE nome_canonico = %s',
                    (match,),
                )
                row = cursor.fetchone()
                if row:
                    produto_id = row[0]
                    print(
                        f'{produto_id}: "{match}" (foi: {old_name}) -> "{new_name}" [FUZZY {score:.0%}]'
                    )
                    updates.append((new_name, produto_id))
                    applied += 1
            else:
                not_found.append(old_name)

    if not_found:
        print()
        print(f'Nao encontrados ({len(not_found)}):')
        for name in not_found:
            print(f'  - {name}')

    if not args.dry_run and updates:
        print()
        print(f'Aplicando {len(updates)} atualizacoes...')
        for new_name, produto_id in updates:
            cursor.execute(
                'UPDATE analytics.dim_produto SET nome_canonico = %s WHERE produto_id = %s',
                (new_name, produto_id),
            )
        conn.commit()
        print(f'[OK] {len(updates)} produtos atualizados com sucesso.')
    elif args.dry_run:
        print()
        print('Dry run ativado. Nenhuma alteracao foi aplicada.')

    cursor.close()
    conn.close()


if __name__ == '__main__':
    main()
