with source as (

    select *
    from {{ source('tse', 'tse_votacao_nominal_municipio_zona') }}

),

renamed as (

    select distinct
        SAFE_CAST(ANO_ELEICAO as int)       as election_year,
        SAFE_CAST(CD_ELEICAO as int64)      as election_id,
        SAFE_CAST(SQ_CANDIDATO as string)   as candidate_id,
        SAFE_CAST(NM_CANDIDATO as string)   as candidate_name,
        NM_URNA_CANDIDATO                   as candidate_ballot_name,
        SAFE_CAST(NR_PARTIDO as int)        as party_id,
        SAFE_CAST(SG_PARTIDO as string)     as party_acr, --Existe só pra faciliar a leitura
        SAFE_CAST(CD_CARGO as int)          as office_id
    from source
)

select *
from renamed
