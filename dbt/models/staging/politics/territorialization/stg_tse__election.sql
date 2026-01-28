with source as (

    select *
        from {{ source('tse', 'tse_votacao_nominal_municipio_zona') }}

),

renamed as (

    select  SAFE_CAST(ANO_ELEICAO AS INT64)             AS election_year,
		SAFE_CAST(CD_ELEICAO AS INT64)					AS election_id,
		SAFE_CAST(NR_TURNO AS INT64)                    AS election_round,
		lower(trim(ds_eleicao))         				AS election_desc,
		SAFE.PARSE_DATE('%d/%m/%Y', DT_ELEICAO)		    AS election_date
    from source

)

select
    *
from renamed
