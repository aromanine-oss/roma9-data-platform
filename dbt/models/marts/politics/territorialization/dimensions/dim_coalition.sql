{{ config(
    materialized = 'incremental',
    unique_key = 'coalition_sk',
    on_schema_change = 'fail'
) }}

with source as (

    select
        coalition_id,
        election_year,
        election_round,
        state_abbreviation,
        coalition_type,
        coalesce(coligation_name, federation_name) as coalition_name
    from {{ ref('stg_tse__coalizao') }}

),

deduplicated as (

    /*
      Remove duplicação entre turnos quando não há
      mudança semântica na coalizão.
      coalition_id é ignorado pois o TSE gera
      identificadores distintos para PARTIDO ISOLADO.
    */
    select
        *,
        row_number() over (
            partition by
                --coalition_id, -- commented to avoid duplicates when the same coalition_name 'PARTIDO ISOLADO' appears in different years. It's ok to have to use only these attributes to identify unique coalitions
                election_year,
                state_abbreviation,
                coalition_type,
                coalition_name
            order by election_round
        ) as rn
    from source

)

select
    -- Natural key
    {{ dbt_utils.generate_surrogate_key([
        'election_year',
        'state_abbreviation',
        'coalition_name',
        'coalition_type',
        
    ]) }} as coalition_nk,

    -- Surrogate key
    {{ dbt_utils.generate_surrogate_key([
        'election_year',
        'state_abbreviation',
        'coalition_name',
        'coalition_type'
    ]) }} as coalition_sk,

    coalition_id, -- kept for lineage/debug
    coalition_name,
    coalition_type,
    election_year,
    state_abbreviation,

    current_timestamp as created_at,
    current_timestamp as updated_at

from deduplicated
where rn = 1
