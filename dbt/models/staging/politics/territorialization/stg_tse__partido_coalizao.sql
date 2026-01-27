with source as (

    select *
    from {{ source('tse', 'tse_votacao_nominal_municipio_zona') }}

),

renamed as (

    select distinct
        safe_cast(ano_eleicao as int64)                as election_year,
        sg_uf                                          as state_abbreviation,

        safe_cast(nr_partido as int64)                 as party_id,

        -- Natural key of coalition (not federation).
        -- Same SQ_COLIGACAO can persist across election rounds.
        safe_cast(sq_coligacao as int64)               as coalition_id,

        case
            when nm_coligacao = 'FEDERAÇÃO' then null
            when nm_coligacao = 'PARTIDO ISOLADO' then 'Partido Isolado'
            else nm_coligacao
        end                                            as coligation_name,

        ds_composicao_coligacao                        as coligation_decomp,

        safe_cast(nullif(nr_federacao, '-1') as int64) as federation_id,
        nullif(nm_federacao, '#NULO#')                 as federation_name,
        nullif(ds_composicao_federacao, '#NULO#')      as federation_decomp

    from roma9-data-platform.roma9_raw.tse_votacao_nominal_municipio_zona

)

select *
from renamed
