{{ config(
    materialized='table',
    unique_key='party_sk'
) }}

with
/* ---------------------------------------------------------------------
   1. Coleta todos os partidos que EXISTEM NO DOMÍNIO ELEITORAL
      (inclusive os que só aparecem via candidato)
--------------------------------------------------------------------- */
party_coverage as (

    select distinct
        party_id,
        election_year
    from {{ ref('stg_tse__candidato') }}

    union distinct

    select distinct
        party_id,
        election_year
    from {{ ref('stg_tse__partido') }}

),

/* ---------------------------------------------------------------------
   2. Enriquecimento com atributos do partido
--------------------------------------------------------------------- */
party_attributes as (

    select
        c.party_id,
        c.election_year,

        p.party_number,
        p.party_name,
        p.party_acr
    --    p.party_status

    from party_coverage c
    left join {{ ref('stg_tse__partido') }} p
        on  c.party_id = p.party_id
        and c.election_year = p.election_year
),

/* ---------------------------------------------------------------------
   3. Detecção de mudança (SCD2)
--------------------------------------------------------------------- */
scd_detection as (

    select
        *,
        lag(party_name) over w as prev_party_name,
        lag(party_acr) over w as prev_party_acr
            from party_attributes
    window w as (
        partition by party_id
        order by election_year
    )

),

/* ---------------------------------------------------------------------
   4. Criação das versões
--------------------------------------------------------------------- */
scd_versions as (

    select
        *,
        case
            when prev_party_name        is distinct from party_name
              or prev_party_acr         is distinct from party_acr
                then 1
            else 0
        end as has_changed
    from scd_detection
   --where has_changed = 1 or prev_party_name is null
),

/* ---------------------------------------------------------------------
   5. Datas de validade baseadas em election_year
--------------------------------------------------------------------- */
final as (

    select
        {{ dbt_utils.generate_surrogate_key([
            'party_id',
            'cast(election_year as string)'
        ]) }} as party_sk,

        party_id,
        election_year,

        party_number,
        party_name,
        party_acr,
        
        election_year as valid_from,
        lead(election_year) over (
            partition by party_id
            order by election_year
        ) - 1 as valid_to,

        case
            when lead(election_year) over (
                partition by party_id
                order by election_year
            ) is null then true
            else false
        end as is_current

    from scd_versions
    where has_changed = 1 or prev_party_name is null
)

select *
from final

{% if is_incremental() %}
where election_year >= (
    select max(election_year) from {{ this }}
)
{% endif %}
