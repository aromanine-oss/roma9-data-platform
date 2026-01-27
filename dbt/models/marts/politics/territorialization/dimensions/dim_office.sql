{{ 
  config(
    materialized = 'table'
  ) 
}}

with source as (

    select
        office_id,
        office_name
    from {{ ref('stg_tse__office') }}

),

deduplicated as (

    select
        {{ dbt_utils.generate_surrogate_key(['office_id']) }} as office_key,
        office_id,
        office_name,
        row_number() over (
            partition by office_id
            order by office_name
        ) as rn
    from source

)

select
    office_key,
    office_id,
    office_name
from deduplicated
where rn = 1
