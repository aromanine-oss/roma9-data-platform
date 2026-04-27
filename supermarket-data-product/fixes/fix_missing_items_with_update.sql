CREATE SCHEMA IF NOT EXISTS staging;

DROP TABLE IF EXISTS staging.stg_nf_item_audit_update_preview;

CREATE TABLE staging.stg_nf_item_audit_update_preview AS
WITH targets AS (
    SELECT
        s.id_nota,
        s.item_index,
        s.produto,
        s.codigo_produto,
        s.quantidade AS quantidade_atual,
        s.valor_total AS valor_total_atual,
        a.missing_count,
        a.quantidade AS quantidade_faltante_unitaria,
        a.valor_total AS valor_total_faltante_unitario
    FROM staging.stg_nf_item s
    JOIN staging.stg_nf_item_audit_missing_products a
      ON a.id_nota = s.id_nota
     AND COALESCE(a.produto, '') = COALESCE(s.produto, '')
     AND COALESCE(a.codigo_produto, '') = COALESCE(s.codigo_produto, '')
     AND COALESCE(a.quantidade, '') = COALESCE(s.quantidade, '')
     AND COALESCE(a.valor_unit, '') = COALESCE(s.valor_unit, '')
     AND COALESCE(a.valor_total, '') = COALESCE(s.valor_total, '')
), ranked AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY id_nota, produto, codigo_produto, quantidade_atual, valor_total_atual
            ORDER BY item_index
        ) AS rn
    FROM targets
)
SELECT
    id_nota,
    item_index,
    produto,
    codigo_produto,
    quantidade_atual,
    valor_total_atual,
    missing_count,
    quantidade_faltante_unitaria,
    valor_total_faltante_unitario,
    REPLACE(
        TO_CHAR(
            (
                COALESCE(REPLACE(quantidade_atual, ',', '.')::numeric, 0) +
                (
                    COALESCE(REPLACE(quantidade_faltante_unitaria, ',', '.')::numeric, 0) *
                    COALESCE(missing_count, 0)
                )
            ),
            'FM9999999990.####'
        ),
        '.',
        ','
    ) AS nova_quantidade,
    REPLACE(
        TO_CHAR(
            (
                COALESCE(REPLACE(valor_total_atual, ',', '.')::numeric, 0) +
                (
                    COALESCE(REPLACE(valor_total_faltante_unitario, ',', '.')::numeric, 0) *
                    COALESCE(missing_count, 0)
                )
            ),
            'FM9999999990.00'
        ),
        '.',
        ','
    ) AS novo_valor_total
FROM ranked
WHERE rn = 1;

UPDATE staging.stg_nf_item s
SET
    quantidade = p.nova_quantidade,
    valor_total = p.novo_valor_total
FROM staging.stg_nf_item_audit_update_preview p
WHERE s.id_nota = p.id_nota
  AND s.item_index = p.item_index;

SELECT *
FROM staging.stg_nf_item_audit_update_preview
ORDER BY id_nota, item_index;
