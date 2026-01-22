with base as (

    select
         state_abbreviation
        ,municipality_id
        ,zone_number

        ,candidate_id
        ,office_id
        ,party_acr
                
        ,election_year
        ,election_round

        ,qty_votes
        ,qty_valid_votes

    from {{ ref('stg_tse__votacao_nominal') }}

    where zone_number is not null

),

territory as (

    select
        territory_sk,
        state_abbreviation,
        municipality_id,
        zone_number
    from {{ ref('dim_territory') }}

),

final as (

    select
        t.territory_sk,

        {{ dbt_utils.generate_surrogate_key([
            'b.candidate_id',
            'b.party_acr'
        ]) }}                     as candidate_sk,

        {{ dbt_utils.generate_surrogate_key([
            'b.party_acr'
        ]) }}                     as party_sk,

        {{ dbt_utils.generate_surrogate_key([
            'b.office_id'
        ]) }}                     as office_sk,

        {{ dbt_utils.generate_surrogate_key([
            'b.election_year',
            'b.election_round'
        ]) }}                     as election_sk,

        b.qty_votes,
        b.qty_valid_votes,
        current_timestamp()       as ingested_at
    from base b
    join territory t
      on b.state_abbreviation = t.state_abbreviation
     and b.municipality_id = t.municipality_id
     and b.zone_number = t.zone_number

)

select
    territory_sk,
    candidate_sk,
    party_sk,
    office_sk,
    election_sk,
    sum(qty_votes)        as qty_votes,
    sum(qty_valid_votes) as qty_valid_votes,
    max(current_timestamp()) as ingested_at
 from final
group by
    territory_sk,
    candidate_sk,
    party_sk,
    office_sk,
    election_sk
