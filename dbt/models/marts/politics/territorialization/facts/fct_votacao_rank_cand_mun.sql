with base as (
    select
        *
    from {{ ref('int_votacao_nominal') }}
),
ranking_candidato as (
select
    election_key,   
    office_key,
    territory_key,
    coalition_key ,
    candidate_key,
    qty_nominal_votes,
    dense_rank() over (partition by election_key, office_key, territory_key order by qty_nominal_votes desc) as rank_candidato
from base
where candidate_key IS NOT NULL
),
total_votos_municipio as (
    select
        election_key,   
        office_key,
        territory_key,
        sum(qty_nominal_votes) as total_votos_municipio
    from base
    group by election_key, office_key, territory_key
    having sum(qty_nominal_votes) > 0 --Ignore cases with zero votes to avoid division by zero in the next step. These cases occur for states that have ZZ abreviation and represent votes cast outside of the municipality, which should not be considered in the competitiveness calculation.
)
select
    ranking_candidato.*,
    total_votos_municipio.total_votos_municipio,
    ranking_candidato.qty_nominal_votes / total_votos_municipio.total_votos_municipio as pct_votos_municipio
from ranking_candidato
    join total_votos_municipio using (election_key, office_key, territory_key)