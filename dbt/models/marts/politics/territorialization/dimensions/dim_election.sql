{{ 
  config(
    materialized = 'table'
  ) 
}}

with source as (

    select
        election_id,
        election_year,
        election_round,
        election_desc,
        election_date
    from {{ ref('stg_tse__election') }}

),

deduplicated as (

    select
        {{ dbt_utils.generate_surrogate_key(['election_year','election_id','election_round', 'election_desc']) }} as election_key,
        election_id,
        election_year,
        election_round,
        election_desc,
        election_date,
        row_number() over (
            partition by election_year,election_id,election_round, election_desc
            order by election_id
        ) as rn
    from source

)

select
    election_key,
    election_id,
    election_year,
    election_round,
    election_desc,
    election_date
from deduplicated
where rn = 1
