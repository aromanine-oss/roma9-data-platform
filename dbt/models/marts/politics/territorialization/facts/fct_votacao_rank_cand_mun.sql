with base as (
    select
        *
    from {{ ref('int_votacao_nominal') }}
)

select
    election_key,   
    candidate_key,
    office_key,
    coalition_key ,
    territory_key,
    qty_nominal_votes,
    dense_rank() over (
        partition by election_key, office_key, territory_key
        order by qty_nominal_votes desc
    ) as rank_candidato
from base
where candidate_key IS NOT NULL 