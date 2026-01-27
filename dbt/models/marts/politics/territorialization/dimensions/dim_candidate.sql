{{ 
  config(
    materialized = 'table'
  ) 
}}

with source as (

    select
            election_year,	
            election_id,
            candidate_id,
            candidate_name,
            candidate_ballot_name,
            party_id,
            party_acr,
            office_id,
    from {{ ref('stg_tse__candidato') }}

),

deduplicated as (

    select
        {{ dbt_utils.generate_surrogate_key(['election_id', 'election_year', 'candidate_id', 'party_id','office_id']) }} as candidate_key,
            election_year,
            election_id,
            candidate_id,
            candidate_name,
            candidate_ballot_name,
            party_id,
            party_acr,
            office_id,
        row_number() over (
            partition by candidate_id, election_id, election_year, party_id, office_id
            order by candidate_id
        ) as rn
    from source

)

select
    candidate_key,
    candidate_id,
    election_id,
    election_year,
    candidate_name,
    candidate_ballot_name,
    party_id,
    party_acr,
    office_id
from deduplicated
where rn = 1
