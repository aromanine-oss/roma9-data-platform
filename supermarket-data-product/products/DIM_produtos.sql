-- =============================================================
-- DIMENSÃO DE PRODUTOS - gerada a partir de notas fiscais
-- =============================================================

-- 1. Tabela de categorias
-- =============================================================
CREATE TABLE IF NOT EXISTS analytics.dim_categoria_produto (
    categoria_id   SERIAL PRIMARY KEY,
    nome_categoria TEXT NOT NULL
);

INSERT INTO analytics.dim_categoria_produto (nome_categoria) VALUES
    ('Frutas e Verduras'),
    ('Carnes e Aves'),
    ('Frios e Laticínios'),
    ('Padaria e Confeitaria'),
    ('Mercearia e Grãos'),
    ('Bebidas não Alcoólicas'),
    ('Bebidas Alcoólicas'),
    ('Doces e Chocolates'),
    ('Congelados e Semi-prontos'),
    ('Limpeza e Higiene'),
    ('Utilidades Domésticas'),
    ('Pets');


-- 2. Tabela de produtos (dimensão)
-- =============================================================
CREATE TABLE IF NOT EXISTS analytics.dim_produto (
    produto_id      SERIAL PRIMARY KEY,
    nome_canonico   TEXT NOT NULL,
    categoria_id    INT  REFERENCES dim_categoria_produto(categoria_id)
);

INSERT INTO analytics.dim_produto (nome_canonico, categoria_id) VALUES
-- Frutas e Verduras (categoria_id = 1)
    ('Abacate / Avocado',           1),
    ('Abobrinha',                   1),
    ('Alho-poró',                   1),
    ('Batata Salsa',                1),
    ('Berinjela',                   1),
    ('Cebola',                      1),
    ('Cebola Flocos (Tempero)',      1),
    ('Cebolinha',                   1),
    ('Cenoura',                     1),
    ('Laranja Bahia',               1),
    ('Limão com Ervas',             1),
    ('Maçã Pink Lady',              1),
    ('Manga Palmer',                1),
    ('Mix Salada',                  1),
    ('Mix Sopa Verde',              1),
    ('Moranga Cabotiá',             1),
    ('Pera Williams',               1),
    ('Salsa em Flocos',             1),
    ('Tangerina',                   1),
    ('Tomate',                      1),
    ('Uva Verde',                   1),
    ('Banana Prata',                1),
    ('Chuchu',                      1),
    ('Alface',                      1),

-- Carnes e Aves (categoria_id = 2)
    ('Embutido de Pernil',          2),
    ('Filé Mignon Suíno',           2),
    ('Lombo Suíno Seara',           2),
    ('Patinho Moído Bovino',        2),
    ('Peito de Frango',             2),
    ('Presunto',                    2),
    ('Sobrecoxa de Frango',         2),

-- Frios e Laticínios (categoria_id = 3)
    ('Iogurte',                     3),
    ('Leite UHT Integral',          3),
    ('Creme de Leite UHT',          3),
    ('Queijo Coalho',               3),
    ('Queijo Mussarela',            3),
    ('Queijo Parmesão',             3),
    ('Queijo Prato',                3),
    ('Requeijão',                   3),
    ('Ricota',                      3),

-- Padaria e Confeitaria (categoria_id = 4)
    ('Biscoito Polvilho',           4),
    ('Biscoito Salgado',            4),
    ('Bolo de Páscoa com Frutas',   4),
    ('Bolo de Páscoa com Gotas',    4),
    ('Butter Cookies',              4),
    ('Pão Francês',                 4),
    ('Pão Integral',                4),
    ('Pão de Batata',               4),

-- Mercearia e Grãos (categoria_id = 5)
    ('Açúcar União',                5),
    ('Aveia em Flocos',             5),
    ('Azeitona',                    5),
    ('Café Arara',                  5),
    ('Café Melitta',                5),
    ('Chá Leão',                    5),
    ('Feijão Branco',               5),
    ('Feijão Fradinho',             5),
    ('Ghee',                        5),
    ('Grão de Bico',                5),
    ('Macarrão',                    5),
    ('Maionese Heinz',              5),
    ('Maionese Hellmanns',          5),
    ('Maionese Maille',             5),
    ('Milho em Lata Knorr',         5),
    ('Molho Ajinomoto',             5),
    ('Molho de Tomate',             5),
    ('Quirera de Arroz',            5),
    ('Tapioca',                     5),
    ('Vinagre de Álcool',           5),
    ('Batata Palha',                5),
    ('Bicarbonato de Sódio',        5),

-- Pets (categoria_id = 12)
    ('Pedigree Tasty',              12),

-- Bebidas não Alcoólicas (categoria_id = 6)
    ('Água de Coco',                6),
    ('Água Mineral',                6),
    ('Água Tônica Schweppes',       6),
    ('Bebida Crystal',              6),
    ('Bebida de Aveia',             6),
    ('Bebida Proteica',             6),
    ('Refrigerante Coca-Cola',      6),
    ('Refrigerante H2OH Limoneto',  6),
    ('Refrigerante Sprite',         6),
    ('Suco',                        6),

-- Bebidas Alcoólicas (categoria_id = 7)
    ('Cerveja Budweiser',           7),
    ('Cerveja Heineken',            7),
    ('Cerveja Caracu',              7),
    ('Vinho Alto Los Romeros',      7),
    ('Vinho Branco Chileno',        7),
    ('Vinho Cremashi',              7),
    ('Vinho Tinto Português',       7),
    ('Vinho Undurraga',             7),

-- Doces e Chocolates (categoria_id = 8)
    ('Barra de Chocolate ao Leite', 8),
    ('Barra de Chocolate Branco c/ Pistache', 8),
    ('Big Mentos Tutti Frutti',     8),
    ('Bombom Bacio',                8),
    ('Bombom Lacta Favoritos',      8),
    ('Bombom Nestlé',               8),
    ('Bombom Sonho de Valsa',       8),
    ('Chocolate Milka',             8),
    ('Ovo de Chocolate Amargo',     8),
    ('Tâmaras com Chocolate',       8),

-- Congelados e Semi-prontos (categoria_id = 9)
    ('Lasanha Sadia 4 Queijos',     9),
    ('Lasanha Sadia Bolonhesa',     9),
    ('Lasanha Sadia Calabresa',     9),
    ('Nuggets de Frango Sadia',     9),
    ('Ovo de Galinha Branco',       9),
    ('Ovo de Galinha Vermelho',     9),
    ('Salsicha Sadia Hot Dog',      9),
    ('Salsicha Seara',              9),

-- Limpeza e Higiene (categoria_id = 10)
    ('Amaciante Ypê L''Occitane',   10),
    ('Limpa Sanitário Pato Marine', 10),
    ('Papel Higiênico',             10),
    ('Sabão em Pó',                 10),

-- Utilidades Domésticas (categoria_id = 11)
    ('Organizador de Geladeira',    11),
    ('Porta Pão',                   11);


-- 3. Tabela de mapeamento: descrição original → produto_id
-- =============================================================
CREATE TABLE IF NOT EXISTS analytics.dim_produto_descricao (
    descricao   TEXT PRIMARY KEY,
    produto_id  INT  REFERENCES dim_produto(produto_id)
);

INSERT INTO analytics.dim_produto_descricao (descricao, produto_id)
SELECT d.descricao, p.produto_id
FROM analytics.dim_produto p
JOIN (VALUES
    ('AVOCADO KG',                                          'Abacate / Avocado'),
    ('ABACATE KG',                                          'Abacate / Avocado'),
    ('ABACATE AVOCAD',                                      'Abacate / Avocado'),
    ('ABOBRINHA BRAN',                                      'Abobrinha'),
    ('ABOBRINHA ITALIANA KG',                               'Abobrinha'),
    ('ALHO PORO KG',                                        'Alho-poró'),
    ('BAT SALSA VDE',                                       'Batata Salsa'),
    ('BERINJELA RAJA',                                      'Berinjela'),
    ('CEBOLA KG',                                           'Cebola'),
    ('CEBOLA kg',                                           'Cebola'),
    ('CEBOLA FLOCOS ROX',                                   'Cebola Flocos (Tempero)'),
    ('CEBOLA EM FLOCOS',                                    'Cebola Flocos (Tempero)'),
    ('CEBOLINHA VDE.',                                      'Cebolinha'),
    ('CENOURA KG',                                          'Cenoura'),
    ('LARANJA BAHIA IMPORTADA KG',                          'Laranja Bahia'),
    ('LIMAO COM ERVAS K',                                   'Limão com Ervas'),
    ('MACA PINK LADY KG',                                   'Maçã Pink Lady'),
    ('MANGA PALMER KG',                                     'Manga Palmer'),
    ('MIX SALADA 200',                                      'Mix Salada'),
    ('MIX SOPA VERDE',                                      'Mix Sopa Verde'),
    ('MORANGA KABOTIA PEDACO KG',                           'Moranga Cabotiá'),
    ('PERA WILLIANS',                                       'Pera Williams'),
    ('SALSA EM FLOCOS',                                     'Salsa em Flocos'),
    ('TANGERINA SALU',                                      'Tangerina'),
    ('TOMATE kg',                                           'Tomate'),
    ('UVA VERDE DOCE',                                      'Uva Verde'),
    ('EMBUTIDO DE PERNIL C',                                'Embutido de Pernil'),
    ('FILE MIG SUI SULITA GOUR SO TEMP RES',                'Filé Mignon Suíno'),
    ('LOMBO TIP CANAD DEF(FAT)SEARA GOURMET',               'Lombo Suíno Seara'),
    ('LOMBO SUINO SEARA (PECA) RE PROMOCAO',                'Lombo Suíno Seara'),
    ('PATINHO MOIDO BOV ARGUS (P) PROMOCAO',                'Patinho Moído Bovino'),
    ('PEITO SOSSO S',                                       'Peito de Frango'),
    ('PRESUNTO CERAT',                                      'Presunto'),
    ('PRESUNTO COZIDO (FATIADO) SADIA KG',                  'Presunto'),
    ('SOBRECOXA FRANGO SADIA CONG PROMOCAO',                'Sobrecoxa de Frango'),
    ('SOBRECOXA COM',                                       'Sobrecoxa de Frango'),
    ('IOG PARC DESN MOR Z',                                 'Iogurte'),
    ('IOG PEDACOS MORANGO',                                 'Iogurte'),
    ('IOG PENSE ZERO BATID',                                'Iogurte'),
    ('LEITE UHT INT PARMAL',                                'Leite UHT Integral'),
    ('QUEIJO COALHO ANILA',                                 'Queijo Coalho'),
    ('*PRO QUEIJO MUSSARELA GALBANI FA PROMOCAO',           'Queijo Mussarela'),
    ('QJ MUSS INTERFOLHADA',                                'Queijo Mussarela'),
    ('QUEIJO PARMESAO FRAC',                                'Queijo Parmesão'),
    ('*PRO QUEIJO PRESIDENT PRATO GRAN PROMOCAO',           'Queijo Prato'),
    ('REQ.DANUBIO LI',                                      'Requeijão'),
    ('CR RICOTA PRES',                                      'Ricota'),
    ('ROSQUINHA ANG POLVILHO (I) KG',                       'Biscoito Polvilho'),
    ('BISC SALGADO GOLDEN',                                 'Biscoito Salgado'),
    ('BOLO DE PASCOA FRUTA',                                'Bolo de Páscoa com Frutas'),
    ('BOLO DE PASCOA GOTAS',                                'Bolo de Páscoa com Gotas'),
    ('BUTTER COOKIES DANIS',                                'Butter Cookies'),
    ('BISC A CASA DO CROISSANT POLV TRAD 80',               'Butter Cookies'),
    ('PAO ANG FRANCES KG',                                  'Pão Francês'),
    ('PAO 47 INTEGR',                                       'Pão Integral'),
    ('PAO BAUDUCCO 36INT FERM NAT PROMOCAO',                'Pão Integral'),
    ('PAO NINO FERM NAT INT CASTQUINOA 400G',               'Pão Integral'),
    ('SOPA DE LEGUME',                                       'Mix Sopa Verde'),
    ('ABOB.CABOTIA D',                                       'Moranga Cabotiá'),
    ('ABOBRINHA VERD',                                       'Abobrinha'),
    ('BANANA PRATA',                                         'Banana Prata'),
    ('BATATA PALHA YOKI T',                                  'Batata Palha'),
    ('BEBIDA VEGETAL CH',                                    'Bebida de Aveia'),
    ('BICARBONATO DE SO',                                    'Bicarbonato de Sódio'),
    ('CENOURA kg',                                           'Cenoura'),
    ('CERV CARACU LT 350ML',                                 'Cerveja Caracu'),
    ('CHUCHU kg',                                            'Chuchu'),
    ('CREME LEITE UHT FRIM',                                 'Creme de Leite UHT'),
    ('LARANJA IMPORT',                                       'Laranja Bahia'),
    ('MIX SALADA BER',                                       'Mix Salada'),
    ('OVO EXTRA BRANCO GRA',                                 'Ovo de Galinha Branco'),
    ('OVOS CAIPIRA LIVRE G',                                 'Ovo de Galinha Vermelho'),
    ('PAO BATATA MIN',                                       'Pão de Batata'),
    ('PAO FRANCES kg',                                       'Pão Francês'),
    ('PAO SEMI ITALI',                                       'Pão Integral'),
    ('PEDIGREE TASTY',                                       'Pedigree Tasty'),
    ('PRESUNTO MACIN',                                       'Presunto'),
    ('QJ.PRATO BOM D',                                       'Queijo Prato'),
    ('QJO PARMESAO ARGENTI',                                 'Queijo Parmesão'),
    ('REFRIG COCA COLA 600',                                 'Refrigerante Coca-Cola'),
    ('REQ VIGOR LIGH',                                       'Requeijão'),
    ('SACHE PROTEINA CH',                                    'Bebida Proteica'),
    ('SALADA ALFACE',                                        'Alface'),
    ('SALS.SEARA LON',                                       'Salsicha Seara'),
    ('SUCO MANGA MACA CAMP',                                 'Suco'),
    ('ACUCAR UNIAO R',                                      'Açúcar União'),
    ('AVEIA FLOCOS FINOS M',                                'Aveia em Flocos'),
    ('AZ.MAMMA BIA 0',                                      'Azeitona'),
    ('CAFE ARARA TM',                                       'Café Arara'),
    ('CAFE MELITTA MOGIANA PCT 250G',                       'Café Melitta'),
    ('CHA LEAO AMOM',                                       'Chá Leão'),
    ('FEIJAO BRANCO AR',                                    'Feijão Branco'),
    ('FEIJAO FRADINHO',                                     'Feijão Fradinho'),
    ('GHEE DOURADINHO 5',                                   'Ghee'),
    ('GRAO DE BICO SUAVE 4',                                'Grão de Bico'),
    ('MAC.ITA.MAMMA',                                       'Macarrão'),
    ('MAC.MAMMA BIA',                                       'Macarrão'),
    ('MAIONESE HEINZ',                                      'Maionese Heinz'),
    ('MAIONESE HELLM',                                      'Maionese Hellmanns'),
    ('MAION.HEL.L600',                                      'Maionese Hellmanns'),
    ('MAIONESE MAILLE FINE',                                'Maionese Maille'),
    ('MILHO KNORR.LT',                                      'Milho em Lata Knorr'),
    ('MOLHO AJI-NO S',                                      'Molho Ajinomoto'),
    ('MOLHO TOMATE H',                                      'Molho de Tomate'),
    ('QUIRERA DE ARROZ',                                    'Quirera de Arroz'),
    ('TAPIOCA TERRINHA NA',                                  'Tapioca'),
    ('VINAGRE DE ALCOOL 6',                                 'Vinagre de Álcool'),
    ('AGUA DE COCO INT CAM',                                'Água de Coco'),
    ('AG MIN SAO LOURENCO',                                 'Água Mineral'),
    ('AGUA MINERAL AGUA PURA CGAS PET 500ML',               'Água Mineral'),
    ('.AGUA TIMBU 5L',                                      'Água Mineral'),
    ('AGUA TONICA SCHWEPPES ZACUCAR LT 220M',               'Água Tônica Schweppes'),
    ('SCHWEPP TON ZE',                                      'Água Tônica Schweppes'),
    ('AGUA TONICA FY',                                      'Água Tônica Schweppes'),
    ('BEB CRYSTAL LIMAO CGAS 510ML',                        'Bebida Crystal'),
    ('BEB CRYSTAL SP',                                      'Bebida Crystal'),
    ('BEBIDA AVEIA NAVEIA',                                 'Bebida de Aveia'),
    ('BEBIDA PROTEIN 15',                                   'Bebida Proteica'),
    ('REFRIG COCA COLA ZER',                                'Refrigerante Coca-Cola'),
    ('REF COCA COLA VIDRO',                                 'Refrigerante Coca-Cola'),
    ('REFRIG SAB H2OH LIMONETO PET 500ML',                  'Refrigerante H2OH Limoneto'),
    ('REFRIG SPRITE LEMON FRESH PET 510ML',                 'Refrigerante Sprite'),
    ('SUCO FESTVAL L',                                      'Suco'),
    ('CERV.BUDWEISER',                                      'Cerveja Budweiser'),
    ('CERVEJA BUDWEISER LT',                                'Cerveja Budweiser'),
    ('CERV HEINEKEN LN 6X3',                                'Cerveja Heineken'),
    ('VHO ALTO LOS ROMEROS',                                'Vinho Alto Los Romeros'),
    ('VHO BCO CHI MANTO BL',                                'Vinho Branco Chileno'),
    ('VHO CREMASHI C',                                      'Vinho Cremashi'),
    ('VHO TTO POR PEN DAS',                                 'Vinho Tinto Português'),
    ('VHO U UNDURRAGA CARM',                                'Vinho Undurraga'),
    ('BARRA CHOCO AO LEITE',                                'Barra de Chocolate ao Leite'),
    ('BAR CHOC BRAN C PIST',                                'Barra de Chocolate Branco c/ Pistache'),
    ('BIG MENTOS TUTTI FRU',                                'Big Mentos Tutti Frutti'),
    ('BOMBOM BACIO L',                                      'Bombom Bacio'),
    ('BOMBOM LACTA FAVORITOS CX 2 PROMOCAO',                'Bombom Lacta Favoritos'),
    ('BOMBOM NESTLE ESPECIALIDADE PROMOCAO',                 'Bombom Nestlé'),
    ('BOMBOM SONHO V',                                      'Bombom Sonho de Valsa'),
    ('*PRO CHOC MILKA ALPINE MILK BR 9 PROMOCAO',           'Chocolate Milka'),
    ('OVO AMARGO 400G MEMB',                                'Ovo de Chocolate Amargo'),
    ('OVO AO LEITE 400G ME',                                'Ovo de Chocolate Amargo'),
    ('TAMARAS CHOCOLATE LE',                                'Tâmaras com Chocolate'),
    ('*PRO LASANHA SADIA 4 QUEIJOS CX 600G',                'Lasanha Sadia 4 Queijos'),
    ('LASANHA SADIA BOLONHESA CX 350G',                     'Lasanha Sadia Bolonhesa'),
    ('LASANHA SADIA CALABRESA 600G',                        'Lasanha Sadia Calabresa'),
    ('NUGGETS FRANGO SADIA TRADIC PROMOCAO',                'Nuggets de Frango Sadia'),
    ('OVO BRANCO POLPA C 1',                                'Ovo de Galinha Branco'),
    ('OVO VERMELHO IANA GRANDE C30',                        'Ovo de Galinha Vermelho'),
    ('OVOS HAPPY EGG',                                      'Ovo de Galinha Vermelho'),
    ('SALSICHA SADIA HOT DOG 500G',                         'Salsicha Sadia Hot Dog'),
    ('AMAC CONC YPE LOCCIT',                                'Amaciante Ypê L''Occitane'),
    ('LIMP SANIT PATO MARINE TABL PROMOCAO',                'Limpa Sanitário Pato Marine'),
    ('PH PERSONAL VIP FT L',                                'Papel Higiênico'),
    ('MM LAVA ROUPAS LAVAN',                                'Sabão em Pó'),
    ('CJ ORG GELADEIRA FRE',                                'Organizador de Geladeira'),
    ('PORTA PAO',                                           'Porta Pão')
) AS d(descricao, canonical)
ON p.nome_canonico = d.canonical
ON CONFLICT (descricao) DO NOTHING;


-- =============================================================
-- QUERY DE USO - join das notas com a dimensão
-- =============================================================
-- SELECT
--     nf.*,
--     p.nome_canonico,
--     c.nome_categoria
-- FROM notas_fiscais nf
-- LEFT JOIN dim_produto_descricao dpd ON nf.descricao = dpd.descricao
-- LEFT JOIN dim_produto            p   ON dpd.produto_id = p.produto_id
-- LEFT JOIN dim_categoria_produto  c   ON p.categoria_id = c.categoria_id;
