{{ config(materialized='table') }}

with source as (

    select *
    from {{ ref('stg_tse__votacao_nominal') }}

),

final as (

    select
        ----------------------------------------------------------------------
        -- SURROGATE KEYS (espelhando exatamente as dimensões)
        ----------------------------------------------------------------------

        {{ dbt_utils.generate_surrogate_key([
            'source.election_id',
            'source.election_year',
            'source.election_desc'
        ]) }}                                   as election_key,

        {{ dbt_utils.generate_surrogate_key([
            'source.election_id', 
            'source.election_year', 
            'source.candidate_id', 
            'source.party_id',
            'source.office_id'
        ]) }}                                   as candidate_key,

        {{ dbt_utils.generate_surrogate_key([
            'source.office_id'
        ]) }}                                   as office_key,

        {{ dbt_utils.generate_surrogate_key([
            'source.election_year',
            'source.election_round',
            'source.state_abbreviation',
            'source.coalition_id',
            'source.party_id',
            'source.coalition_name',
            'source.coalition_decomp'
        ]) }}                                   as coalition_key,

        {{ dbt_utils.generate_surrogate_key([
        'state_abbreviation',
        'municipality_id',
        'zone_number'
        ]) }}            as territory_key,

        ----------------------------------------------------------------------
        -- MÉTRICAS
        ----------------------------------------------------------------------

        source.qty_votes               as qty_nominal_votes,
        source.qty_valid_votes         as qty_valid_votes

    from source

)

select *
from final
