with source as (

    select *
        from {{ source('tse', 'tse_votacao_nominal_municipio_zona') }}

),

renamed as (

    select distinct
            safe_cast(cd_cargo as int64)                    as office_id,
            safe_cast(ds_cargo as string)                   as office_name

    from source

)

select *
from renamed
