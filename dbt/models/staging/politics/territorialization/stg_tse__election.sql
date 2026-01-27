with source as (

    select *
        from {{ source('tse', 'tse_votacao_nominal_municipio_zona') }}

),

renamed as (

    select distinct
            safe_cast(ano_eleicao as int64)          as election_year,
            safe_cast(cd_eleicao as int64)           as election_id,
            safe_cast(nr_turno as int)               as election_round,
            ds_eleicao                               as election_desc,
            safe.parse_date('%d/%m/%Y', dt_eleicao)  as election_date                           
    from source

)

select --election_id, count(1)
    *
from renamed
--where election_id in (144,143)
--group by renamed.election_id
--having count(1) > 1
--