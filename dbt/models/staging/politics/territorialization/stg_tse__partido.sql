with source as (

    select *
    from {{ source('tse', 'tse_votacao_nominal_municipio_zona') }}

),

renamed as (

    select DISTINCT
        SAFE_CAST(ANO_ELEICAO as INT64)     AS election_year,
        SAFE_CAST(NR_PARTIDO as INT64)      AS party_id,
        SAFE_CAST(NR_PARTIDO as INT64)      AS party_number,
        SG_PARTIDO     AS party_acr,
        --INITCAP(SAFE_CAST(NM_PARTIDO as string))     AS party_name,
        INITCAP(regexp_replace(normalize(NM_PARTIDO, NFD), r'\pM', '')) as party_name
               
    from source
), renamed_filter as (
select *, 
       row_number() over (partition by election_year, party_id order by party_id) as rn
from renamed
)
select *
from renamed_filter
where rn = 1
