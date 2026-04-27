with base as (

    select *
    from {{ ref('fct_votacao_rank_cand_mun') }}

),
topN as (

    select
        election_key,
        office_key,
        territory_key,
        max(case when rank_candidato = 1 then qty_nominal_votes end) as votes_1,
        max(case when rank_candidato = 2 then qty_nominal_votes end) as votes_2,
        sum(case when rank_candidato <= 2 then qty_nominal_votes end) * 1.0 / sum(qty_nominal_votes) as top2_vote_share,
        sum(case when rank_candidato <= 3 then qty_nominal_votes end) * 1.0 / sum(qty_nominal_votes) as top3_vote_share,
        sum(case when rank_candidato <= 5 then qty_nominal_votes end) * 1.0 / sum(qty_nominal_votes) as top5_vote_share
    from base
    where rank_candidato <= 5
    group by
        election_key,
        office_key,
        territory_key

),
pct_diff_1_2 as (
select
    *,
    --(votos_1 - COALESCE(votos_2, votos_1)) * 1.0 / votos_1 as pct_diff_1_2
    case
        when votes_2 is not null then (votes_1 - votes_2) * 1.0 / votes_1
        else 1.0
    end as pct_diff

from topN
)
select
    *,
    --base.qty_nominal_votes,
case
    when votes_2 is null then 'Candidato Único'
    when pct_diff >= 0.5 then 'Alta'
    when pct_diff >= 0.2 then 'Média'
    else 'Baixa'
end as competitiveness
from pct_diff_1_2