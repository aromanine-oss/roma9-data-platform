with base as (

    select *
    from {{ ref('fct_votacao_rank_cand_mun') }}

),

top2 as (

    select
        election_key,
        office_key,
        territory_key,

        max(case when rank_candidato = 1 then qty_nominal_votes end) as votos_1,
        max(case when rank_candidato = 2 then qty_nominal_votes end) as votos_2

    from base
    where rank_candidato <= 2
    group by
        election_key,
        office_key,
        territory_key

)

select
    *,
    --(votos_1 - COALESCE(votos_2, votos_1)) * 1.0 / votos_1 as pct_diff_1_2
    case
        when votos_2 is not null then (votos_1 - votos_2) * 1.0 / votos_1
        else 1.0
    end as pct_diff_1_2

from top2