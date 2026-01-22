select distinct
    {{ dbt_utils.generate_surrogate_key([
        'state_abbreviation',
        'municipality_id',
        'zone_number'
    ]) }}            as territory_sk,

    state_abbreviation,
    municipality_id,
    zone_number

from {{ ref('stg_tse__votacao_nominal') }}
where zone_number is not null
