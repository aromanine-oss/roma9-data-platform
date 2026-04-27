-- =============================================================
-- ADIÇÃO DE PRODUTOS FALTANDO NA DIMENSÃO
-- =============================================================

-- 1. Adicionar novos produtos canônicos em dim_produto
-- =============================================================
INSERT INTO analytics.dim_produto (nome_canonico, categoria_id) VALUES
    ('Areia para Gatos',             12), -- Pets
    ('Atum Sólido',                  5),
    ('Bacon',                        2),  -- Carnes e Aves
    ('Batata a Granel',              1),  -- Frutas e Verduras
    ('Bebida de Castanha',           6),  -- Bebidas não Alcoólicas
    ('Cerveja Blue Moon',            7),  -- Bebidas Alcoólicas
    ('Cerveja Bodebrown',            7),
    ('Cerveja Antarctica',           7),
    ('Cerveja Corona',               7),
    ('Esponja',                      10), -- Limpeza e Higiene
    ('Mini Sal',                     5),  -- Mercearia e Grãos (salgadinho)
    ('Óleo de Canola',               5),
    ('Sacola',                       11); -- Utilidades Domésticas

-- 2. Adicionar mapeamentos em dim_produto_descricao
-- =============================================================
INSERT INTO analytics.dim_produto_descricao (descricao, produto_id)
SELECT d.descricao, p.produto_id
FROM analytics.dim_produto p
JOIN (VALUES
    ('AREIA GATOS KAT BOM 3KG CLINICAL',     'Areia para Gatos'),
    ('ATUM SOLIDO MEMBERS',                  'Atum Sólido'),
    ('BACON DEF BIZZ',                       'Bacon'),
    ('BATATA A GRANE',                       'Batata a Granel'),
    ('BEB TAL DA CASTANHA',                  'Bebida de Castanha'),
    ('BISC POLV QUEIJO 200',                 'Biscoito Polvilho'),
    ('CERV BLUE MOON SLEEK',                 'Cerveja Blue Moon'),
    ('CERV BODEBROWN POPEY',                 'Cerveja Bodebrown'),
    ('CERV BUDWEISER SLEEK',                 'Cerveja Budweiser'),
    ('CERV.ANTAR.ORI',                       'Cerveja Antarctica'),
    ('CORONA EXTRA N LT SL',                 'Cerveja Corona'),
    ('ESPONJA SB NAO RISCA',                 'Esponja'),
    ('MINI SAL ORIGINAL GO',                 'Mini Sal'),
    ('MUSSA FRAC LATELLI P',                 'Queijo Mussarela'),
    ('OLEO CANO LIZA 900ML',                 'Óleo de Canola'),
    ('SACOLA SAMS GRD BRAN',                 'Sacola'),
    ('SOBRE COXA SEM PELE',                  'Sobrecoxa de Frango'),
    ('TAPIOCA 560G MEMBERS',                 'Tapioca')
) AS d(descricao, canonical)
ON p.nome_canonico = d.canonical
ON CONFLICT (descricao) DO NOTHING;